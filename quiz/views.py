from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Answer, UserAnswer
from django.utils import timezone
from tasks.models import VisitorTask
from tasks.views import get_visitor_id
from django.views.decorators.cache import never_cache




def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_list.html', {'quizzes': quizzes})



def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    first_question = quiz.questions.first()
    if not first_question:
        return redirect('quiz:quiz_result', quiz_id=quiz.id)
    # initialize session
    request.session['quiz_index'] = 0
    request.session['quiz_answers'] = {}
    request.session['quiz_id'] = quiz.id
    return redirect('quiz:take_quiz', quiz_id=quiz.id)


@never_cache
def take_quiz(request, quiz_id):
    visitor_id = get_visitor_id(request)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all())
    index = request.session.get("quiz_index", 0)
    answers_dict = request.session.get("quiz_answers", {})

    # Quiz finished
    if index >= len(questions):
        score = 0
        for qid, selected_id in answers_dict.items():
            question = get_object_or_404(Question, id=int(qid))
            selected_answer = get_object_or_404(Answer, id=int(selected_id))
            is_correct = selected_answer.is_correct

            UserAnswer.objects.update_or_create(
                visitor_id=visitor_id,
                question=question,
                defaults={"is_correct": is_correct},
            )

            if is_correct:
                score += 1

        # Cleanup session
        request.session.pop("quiz_index", None)
        request.session.pop("quiz_answers", None)
        request.session.pop("quiz_id", None)

        return render(request, "quiz_result.html", {
            "quiz": quiz,
            "score": score,
            "total": len(questions),
        })

    # Continue quiz
    current_question = questions[index]
    answers = current_question.answers.all()

    if request.method == "POST":
        selected_answer_id = request.POST.get("answer")
        if selected_answer_id:
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

@never_cache
def quiz_result(request, quiz_id):
    visitor_id = get_visitor_id(request)
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user_answers = UserAnswer.objects.filter(visitor_id=visitor_id, question__quiz=quiz)
    score = user_answers.filter(is_correct=True).count()
    total = quiz.questions.count()

    return render(request, "quiz_result.html", {
        "quiz": quiz,
        "score": score,
        "total": total,
    })
