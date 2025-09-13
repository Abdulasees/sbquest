from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task, UserTask
from quiz.models import UserAnswer
from wallet.models import WalletTransaction
from django.views.decorators.cache import never_cache
from django.db import transaction
from zoneinfo import ZoneInfo  # Python 3.9+


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
def assign_tasks(user, slot_start, slot_end):
    """
    Assign fresh tasks only if none exist for this slot and not completed.
    """
    # Check already assigned tasks in this slot
    existing = UserTask.objects.filter(
        user=user,
        assigned_at__gte=slot_start,
        assigned_at__lt=slot_end
    )

    if existing.exists():
        return list(existing)

    # Exclude tasks already completed by user in any slot
    completed_ids = UserTask.objects.filter(
        user=user, completed=True
    ).values_list("task_id", flat=True)

    # Select fresh tasks
    fresh_tasks = list(Task.objects.exclude(id__in=completed_ids).order_by("id")[:BATCH_SIZE])

    assigned_list = []
    ist_now = timezone.now().astimezone(ZoneInfo("Asia/Kolkata"))

    for task in fresh_tasks:
        ut = UserTask.objects.create(user=user, task=task, assigned_at=ist_now)
        assigned_list.append(ut)

    return assigned_list


# -------------------------------
# TASK LIST VIEW
# -------------------------------
@never_cache
@login_required
def task_list(request):
    user = request.user
    slot_start, slot_end = get_slot_times()

    # 1. Get tasks already assigned in this slot
    assigned = UserTask.objects.filter(
        user=user,
        assigned_at__gte=slot_start,
        assigned_at__lt=slot_end
    ).order_by("assigned_at")

    # 2. Assign fresh tasks if none exist
    if not assigned.exists():
        assigned = assign_tasks(user, slot_start, slot_end)

    # 3. Filter only unfinished tasks
    unfinished_tasks = [ut.task for ut in assigned if not ut.completed]

    # 4. If batch is already finished, show empty
    completed_count = UserTask.objects.filter(
        user=user,
        completed=True,
        completed_at__gte=slot_start,
        completed_at__lt=slot_end
    ).count()
    if completed_count >= BATCH_SIZE or not unfinished_tasks:
        return render(request, "task_list.html", {"tasks": []})

    return render(request, "task_list.html", {"tasks": unfinished_tasks})


# -------------------------------
# TASK DETAIL / QUIZ VIEW
# -------------------------------
@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    quiz = task.quiz

    if not quiz:
        return render(request, "task_detail.html", {"task": task, "quiz": None, "questions": None})

    questions = list(quiz.questions.all())
    total_questions = len(questions)
    q_index = int(request.GET.get("q", 0))
    q_index = max(0, min(q_index, total_questions - 1))
    current_question = questions[q_index]
    error = None

    if request.method == "POST":
        selected_answer_id = request.POST.get("answer")
        if selected_answer_id:
            selected_answer = current_question.answers.get(id=selected_answer_id)
            is_correct = selected_answer.is_correct

            UserAnswer.objects.update_or_create(
                user=request.user,
                question=current_question,
                defaults={"is_correct": is_correct},
            )

            if not is_correct:
                error = "Incorrect! Please select the correct answer to continue."
            else:
                # Finish quiz
                if q_index + 1 >= total_questions:
                    slot_start, slot_end = get_slot_times()
                    user_task = UserTask.objects.filter(
                        user=request.user,
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
                                    user=request.user,
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
@login_required
def submit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    slot_start, slot_end = get_slot_times()
    user = request.user

    if task.quiz:
        return redirect("tasks:task_detail", pk=task_id)

    if request.method == "POST":
        # Check completed tasks in this slot
        completed_count = UserTask.objects.filter(
            user=user,
            completed=True,
            completed_at__gte=slot_start,
            completed_at__lt=slot_end,
        ).count()
        if completed_count >= BATCH_SIZE:
            messages.info(request, "You already finished your batch for this slot.")
            return redirect("tasks:task_list")

        # Get the assignment for this task
        user_task = UserTask.objects.filter(
            user=user,
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
                        user=request.user,
                        amount=task.reward_sb,
                        transaction_type="credit",
                        status="approved",
                    )
                    user_task.reward_given = True

                user_task.save()
                messages.success(request, f"You got {task.reward_sb} SB!")
        else:
            messages.info(request, "Task already completed or not assigned in this slot.")

        # Defensive cleanup: remove extra uncompleted assignments
        finished_count = UserTask.objects.filter(
            user=user,
            completed=True,
            completed_at__gte=slot_start,
            completed_at__lt=slot_end
        ).count()
        if finished_count >= BATCH_SIZE:
            UserTask.objects.filter(
                user=user,
                completed=False,
                assigned_at__gte=slot_start,
                assigned_at__lt=slot_end
            ).delete()

        return redirect("tasks:task_list")

    return render(request, "submit_task.html", {"task": task})


# -------------------------------
# TASK TITLES ONLY (Optional)
# -------------------------------
@login_required
def task_titles_only(request):
    tasks = Task.objects.filter(active=True)
    return render(request, "task_titles_only.html", {"tasks": tasks})
