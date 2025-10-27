from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task, VisitorTask

from quiz.models import UserAnswer
from wallet.models import WalletTransaction
from django.views.decorators.cache import never_cache
from django.db import transaction
from zoneinfo import ZoneInfo  # Python 3.9+
import uuid




# -------------------------------
# CONFIG
# -------------------------------
BATCH_SIZE = 2  # Change this number anytime


# -------------------------------
# SLOT LOGIC
# -------------------------------
def get_slot_times():
    """
    Return start and end of the current 12-hour slot in IST.
    Slot 0 = 12 AM–12 PM IST
    Slot 1 = 12 PM–12 AM IST
    """
    now = timezone.now().astimezone(ZoneInfo("Asia/Kolkata"))
    if now.hour < 12:  # Morning slot
        slot_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        slot_end = slot_start + timedelta(hours=12)
    else:  # Afternoon slot
        slot_start = now.replace(hour=12, minute=0, second=0, microsecond=0)
        slot_end = slot_start + timedelta(hours=12)
    return slot_start, slot_end


# -------------------------------
# HELPER: Assign fresh tasks
# -------------------------------
def assign_tasks(visitor_id, slot_start, slot_end):
    """
    Assign fresh tasks only if none exist for this slot and not completed.
    """
    # Check already assigned tasks in this slot
    existing = VisitorTask.objects.filter(
        visitor_id=visitor_id,
        assigned_at__gte=slot_start,
        assigned_at__lt=slot_end
    )

    if existing.exists():
        return list(existing)

    # Exclude tasks already completed by user in any slot
    completed_ids = VisitorTask.objects.filter(
        visitor_id=visitor_id, completed=True
    ).values_list("task_id", flat=True)

    # Select fresh tasks
    fresh_tasks = list(Task.objects.exclude(id__in=completed_ids).order_by("id")[:BATCH_SIZE])

    assigned_list = []
    ist_now = timezone.now().astimezone(ZoneInfo("Asia/Kolkata"))

    half_day = 0 if slot_start.hour == 0 else 1
    assigned_date = slot_start.date()

    for task in fresh_tasks:
        ut = VisitorTask.objects.create(
        visitor_id=visitor_id,
        task=task,
        assigned_at=ist_now,
        assigned_date=assigned_date,  # <-- add this
        half_day=half_day             # <-- add this
    )


        assigned_list.append(ut)

    return assigned_list
def get_visitor_id(request):
    visitor_id = request.session.get('visitor_id')
    if not visitor_id:
        visitor_id = str(uuid.uuid4())
        request.session['visitor_id'] = visitor_id
    return visitor_id


# -------------------------------
# TASK LIST VIEW
# -------------------------------
@never_cache
def task_list(request):
    visitor_id = get_visitor_id(request)

    slot_start, slot_end = get_slot_times()

    # 1. Get tasks already assigned in this slot
    assigned = VisitorTask.objects.filter(
        visitor_id=visitor_id,
        assigned_at__gte=slot_start,
        assigned_at__lt=slot_end,
        completed=False
    ).order_by("assigned_at")

    # 2. Assign fresh tasks if none exist
    if not assigned.exists():
        assigned = assign_tasks(visitor_id, slot_start, slot_end)

    # 3. Filter only unfinished tasks
    unfinished_tasks = [ut.task for ut in assigned if not ut.completed]
    # Get all attempted (completed) tasks by user in this slot
    attempted_tasks = [
        ut.task for ut in assigned if ut.completed
    ]


    # 4. If batch is already finished, show empty
    completed_count = VisitorTask.objects.filter(
        visitor_id=visitor_id,
        completed=True,
        completed_at__gte=slot_start,
        completed_at__lt=slot_end
    ).count()
    if completed_count >= BATCH_SIZE or not unfinished_tasks:
        return render(request, "task_list.html", {
            "tasks": attempted_tasks,  # show completed if slot done
            "attempted_tasks": attempted_tasks
        })

    all_tasks = list(unfinished_tasks) + list(attempted_tasks)

    return render(request, "task_list.html", {
        "tasks": all_tasks,
        "attempted_tasks": attempted_tasks
    })


# -------------------------------
# TASK DETAIL / QUIZ VIEW
# -------------------------------
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    visitor_id = get_visitor_id(request)
    quiz = task.quiz

    if not quiz:
        return render(
            request,
            "task_detail.html",
            {"task": task, "quiz": None, "questions": None}
        )

    questions = list(quiz.questions.all())
    total_questions = len(questions)
    q_index = int(request.GET.get("q", 0))
    q_index = max(0, min(q_index, total_questions - 1))
    current_question = questions[q_index]
    error = None

    if request.method == "POST":
        # ✅ NEW: Handle Back button
        if "back" in request.POST:
            prev_index = max(0, q_index - 1)
            return redirect(f"{request.path}?q={prev_index}")

        selected_answer_id = request.POST.get("answer")
        if selected_answer_id:
            selected_answer = current_question.answers.get(id=selected_answer_id)
            is_correct = selected_answer.is_correct

            UserAnswer.objects.update_or_create(
                visitor_id=visitor_id,
                question=current_question,
                defaults={"is_correct": is_correct},
            )

            if not is_correct:
                error = "Incorrect! Please select the correct answer to continue."
            else:
                # Finish quiz
                if q_index + 1 >= total_questions:
                    slot_start, slot_end = get_slot_times()
                    user_task = VisitorTask.objects.filter(
                        visitor_id = visitor_id,
                        task=task,
                        assigned_at__gte=slot_start,
                        assigned_at__lt=slot_end,
                        completed=False
                    ).order_by("-assigned_at").first()

                    if user_task:
                        with transaction.atomic():
                            user_task.completed = True
                            user_task.completed_at = timezone.now()
                            if not user_task.reward_given:
                                WalletTransaction.objects.create(
                                    visitor_id = visitor_id,
                                    amount=task.reward_sb,
                                    transaction_type="credit",
                                    status="approved",
                                )
                                user_task.reward_given = True
                            user_task.save()
                        messages.success(request, f"You got {task.reward_sb} SB!")

                    return redirect("tasks:task_list")

                return redirect(f"{request.path}?q={q_index + 1}")

    return render(
        request,
        "task_detail.html",
        {
            "task": task,
            "quiz": quiz,
            "question": current_question,
            "answers": current_question.answers.all(),
            "question_number": q_index + 1,
            "total_questions": total_questions,
            "error": error,
        },
    )


# -------------------------------
# SUBMIT TASK VIEW (NON-QUIZ)
# -------------------------------
@never_cache
def submit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    slot_start, slot_end = get_slot_times()
    visitor_id = get_visitor_id(request)


    if task.quiz:
        return redirect("tasks:task_detail", pk=task_id)

    if request.method == "POST":
        # Check completed tasks in this slot
        completed_count = VisitorTask.objects.filter(
            visitor_id=visitor_id,
            completed=True,
            completed_at__gte=slot_start,
            completed_at__lt=slot_end,
        ).count()
        if completed_count >= BATCH_SIZE:
            messages.info(request, "You already finished your batch for this slot.")
            return redirect("tasks:task_list")

        # Get the assignment for this task
        user_task = VisitorTask.objects.filter(
            visitor_id=visitor_id,
            task=task,
            assigned_at__gte=slot_start,
            assigned_at__lt=slot_end,
        ).order_by("-assigned_at").first()

        if user_task and not user_task.completed:
            with transaction.atomic():
                user_task.completed = True
                user_task.completed_at = timezone.now()

                if not user_task.reward_given:
                    WalletTransaction.objects.create(
                        visitor_id=visitor_id,
                        amount=task.reward_sb,
                        transaction_type="task_reward",
                        status="approved",
                    )
                    user_task.reward_given = True

                user_task.save()
                messages.success(request, f"You got {task.reward_sb} SB!")
        else:
            messages.info(request, "Task already completed or not assigned in this slot.")

        # Defensive cleanup: remove extra uncompleted assignments
        finished_count = VisitorTask.objects.filter(
            visitor_id=visitor_id,
            completed=True,
            completed_at__gte=slot_start,
            completed_at__lt=slot_end
        ).count()
        if finished_count >= BATCH_SIZE:
            VisitorTask.objects.filter(
                visitor_id=visitor_id,
                completed=False,
                assigned_at__gte=slot_start,
                assigned_at__lt=slot_end
            ).delete()

        return redirect("tasks:task_list")

    return render(request, "submit_task.html", {"task": task})


# -------------------------------
# TASK TITLES ONLY (Optional)
# -------------------------------
def task_titles_only(request):
    tasks = Task.objects.filter(active=True)
    return render(request, "task_titles_only.html", {"tasks": tasks})
