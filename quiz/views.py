from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Answer, UserAnswer
from django.utils import timezone
from tasks.models import VisitorTask


@login_required
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_list.html', {'quizzes': quizzes})


@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # Always go to the first question
    first_question = quiz.questions.first()
    if not first_question:
        return redirect('quiz:quiz_result', quiz_id=quiz.id)
    return redirect('quiz:take_quiz', quiz_id=quiz.id, question_id=first_question.id)


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all())
    index = request.session.get("quiz_index", 0)

    # ✅ quiz finished
    if index >= len(questions):
        score = 0
        answers = request.session.get("quiz_answers", {})

        for qid, selected in answers.items():
            question = get_object_or_404(Question, id=int(qid))
            selected_answer = get_object_or_404(Answer, id=int(selected))
            is_correct = selected_answer.is_correct

            UserAnswer.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={"selected_answer": selected_answer, "is_correct": is_correct},
            )
            if is_correct:
                score += 1

        # ✅ handle task reward (if quiz is linked to a Task)
        task = getattr(quiz, "task", None)
        points_awarded = 0
        if task:
            user_task, created = VisitorTask.objects.get_or_create(
                user=request.user,
                task=task,
                defaults={
                    "completed": True,
                    "completed_at": timezone.now(),
                    "reward_given": True,
                },
            )
            if not created and not user_task.completed:
                user_task.completed = True
                user_task.completed_at = timezone.now()

            if not user_task.reward_given:
                request.user.points += task.reward_sb
                request.user.save()
                user_task.reward_given = True
                points_awarded = task.reward_sb

            user_task.save()

        # cleanup
        request.session.pop("quiz_index", None)
        request.session.pop("quiz_answers", None)
        request.session.pop("quiz_id", None)

        return render(request, "quiz_result.html", {
            "quiz": quiz,
            "score": score,
            "total": len(questions),
            "points_earned": points_awarded,
            "total_points": request.user.points,
        })

    # ✅ continue quiz
    current_question = questions[index]
    answers = current_question.answers.all()

    if request.method == "POST":
        selected_answer_id = request.POST.get("answer")  # ✅ matches your HTML
        if selected_answer_id:
            answers_dict = request.session.get("quiz_answers", {})
            answers_dict[str(current_question.id)] = selected_answer_id
            request.session["quiz_answers"] = answers_dict
            request.session["quiz_index"] = index + 1
            return redirect("quiz:take_quiz", quiz_id=quiz_id)

    return render(request, "take_quiz.html", {
        "quiz": quiz,
        "question": current_question,
        "answers": answers,
        "question_number": index + 1,
        "total_questions": len(questions),
    })




@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user_answers = UserAnswer.objects.filter(user=request.user, question__quiz=quiz)
    score = user_answers.filter(is_correct=True).count()
    total = quiz.questions.count()

    return render(request, "quiz_result.html", {
        "quiz": quiz,
        "score": score,
        "total": total,
    })
