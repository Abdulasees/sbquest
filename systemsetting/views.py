from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.views.decorators.cache import never_cache
from zoneinfo import ZoneInfo

from .models import DailyOffer, DailyOfferAssignment, DailyOfferAnswer
from wallet.models import WalletTransaction

# -------------------------------
# CONFIG
# -------------------------------
BATCH_SIZE = 1  # Number of offers per slot

# -------------------------------
# SLOT LOGIC (12-hour slots IST)
# -------------------------------
def current_slot():
    """
    Return today's date and current slot (0 = 12 AM–12 PM IST, 1 = 12 PM–12 AM IST)
    """
    now = timezone.now().astimezone(ZoneInfo("Asia/Kolkata"))
    today = now.date()

    if 0 <= now.hour < 12:
        half_day = 0
    else:
        half_day = 1

    return today, half_day

# -------------------------------
# HELPER: Assign fresh offers
# -------------------------------
def assign_offers(user, today, half_day):
    """
    Assign fresh offers only if none exist for this slot.
    """
    existing = DailyOfferAssignment.objects.filter(
        user=user,
        assigned_date=today,
        half_day=half_day
    ).select_related("offer")

    if existing.exists():
        return list(existing)

    # Exclude offers already completed by the user
    completed_ids = DailyOfferAssignment.objects.filter(
        user=user, completed=True
    ).values_list("offer_id", flat=True)

    all_offers = list(DailyOffer.objects.filter(is_active=True).exclude(id__in=completed_ids).order_by("id"))

    if not all_offers:
        return []

    selected = []
    for offer in all_offers[:BATCH_SIZE]:
        assignment = DailyOfferAssignment.objects.create(
            user=user,
            offer=offer,
            assigned_date=today,
            half_day=half_day,
            completed=False,
            reward_given=False,
            failed=False,
        )
        selected.append(assignment)

    return selected

# -------------------------------
# VIEWS
# -------------------------------
@never_cache
@login_required
def daily_offer_list(request):
    today, half_day = current_slot()

    # ✅ 1. Get offers already assigned in this slot
    assignments = DailyOfferAssignment.objects.filter(
        user=request.user,
        assigned_date=today,
        half_day=half_day
    ).select_related("offer")

    # ✅ 2. Assign fresh batch if nothing exists
    if not assignments.exists():
        assignments = assign_offers(request.user, today, half_day)

    # ✅ 3. Enforce batch size
    if len(assignments) > BATCH_SIZE:
        keep_ids = [a.id for a in assignments[:BATCH_SIZE]]
        assignments = [a for a in assignments if a.id in keep_ids]

    # ✅ 4. Show only unfinished offers
    unfinished = [a.offer for a in assignments if not a.completed]

    # ✅ 5. If user completed all in slot → show empty
    if len(unfinished) == 0:
        return render(request, "daily_offer_list.html", {
            "assigned_tasks": [],
            "message": "🎉 Finished all offers for this slot. Come back in the next slot!",
            "batch_size": BATCH_SIZE,
        })

    return render(request, "daily_offer_list.html", {
        "assigned_tasks": unfinished,
        "batch_size": BATCH_SIZE,
    })


@never_cache
@login_required
def claim_offer(request, offer_id, question_index=0):
    today, half_day = current_slot()
    offer = get_object_or_404(DailyOffer, id=offer_id)

    assignment = DailyOfferAssignment.objects.filter(
        user=request.user,
        offer=offer,
        assigned_date=today,
        half_day=half_day
    ).first()

    if not assignment or assignment.completed:
        return redirect("systemsetting:daily_offer_list")

    questions = list(offer.questions.prefetch_related("answers"))
    if not questions:
        return redirect("systemsetting:daily_offer_list")

    total_questions = len(questions)
    question_index = max(0, min(question_index, total_questions - 1))
    current_question = questions[question_index]
    answers = current_question.answers.all()

    if request.method == "POST":
        selected_answer_id = request.POST.get("answer")
        if selected_answer_id:
            try:
                selected_answer = DailyOfferAnswer.objects.get(
                    id=selected_answer_id,
                    question=current_question
                )
            except DailyOfferAnswer.DoesNotExist:
                messages.error(request, "Invalid answer selected.")
                return redirect("systemsetting:claim_offer", offer_id=offer.id, question_index=question_index)

            if not selected_answer.is_correct:
                messages.error(request, "❌ Wrong answer! Try again.")
                return redirect("systemsetting:claim_offer", offer_id=offer.id, question_index=question_index)

            if question_index == total_questions - 1:
                # ✅ Complete assignment and give reward
                with transaction.atomic():
                    assignment = DailyOfferAssignment.objects.select_for_update().get(id=assignment.id)
                    assignment.completed = True
                    assignment.completed_at = timezone.now()

                    if not assignment.reward_given:
                        WalletTransaction.objects.create(
                            user=request.user,
                            amount=offer.reward_sb,
                            transaction_type="daily_offer_reward",
                            status="approved",
                            timestamp=timezone.now()
                        )
                        assignment.reward_given = True
                        messages.success(request, f"🎉 Correct! You earned {offer.reward_sb} SB!")
                    assignment.save()

                return redirect("systemsetting:daily_offer_list")

            messages.success(request, "✅ Correct! Next question.")
            return redirect("systemsetting:claim_offer", offer_id=offer.id, question_index=question_index + 1)

    return render(request, "offer_question.html", {
        "offer": offer,
        "question": current_question,
        "answers": answers,
        "question_index": question_index,
        "total_questions": total_questions
    })
