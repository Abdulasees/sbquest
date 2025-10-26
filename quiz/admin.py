from django import forms
from django.contrib import admin
import nested_admin
from .models import Quiz, Question, Answer, UserAnswer


# --- Form for Question: smaller text box + bulk textarea ---
class QuestionForm(forms.ModelForm):
    bulk_answers = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5, "cols": 40}),
        required=False,
        help_text=(
            "Enter one answer per line. "
            "Prefix the correct one with * (asterisk). Example:\n"
            "*Mango\nApple\nBanana"
        ),
        label="Bulk answers",
    )

    class Meta:
        model = Question
        fields = "__all__"
        widgets = {
            "text": forms.TextInput(attrs={"size": 80}),  # ✅ smaller question box
        }


# --- Answer inline (unlimited answers per Question) ---
class AnswerInline(nested_admin.NestedTabularInline):
    model = Answer
    extra = 0
    fields = ("text", "image", "is_correct")


# --- Question inline (unlimited questions per Quiz) ---
class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    form = QuestionForm
    extra = 1
    inlines = [AnswerInline]


# --- Quiz admin (top-level container) ---
@admin.register(Quiz)
class QuizAdmin(nested_admin.NestedModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    inlines = [QuestionInline]

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)

        if getattr(formset, "model", None) is Question:
            for q_form in formset.forms:
                cd = getattr(q_form, "cleaned_data", None)
                if not cd:
                    continue

                bulk_text = (cd.get("bulk_answers") or "").strip()
                if not bulk_text:
                    continue

                question = q_form.instance

                lines = [ln.strip() for ln in bulk_text.splitlines() if ln.strip()]
                first_starred_text = None

                for line in lines:
                    is_correct = line.startswith("*")
                    text = line[1:].strip() if is_correct else line

                    obj, created = Answer.objects.get_or_create(
                        question=question,
                        text=text,
                        defaults={"is_correct": is_correct},
                    )
                    if not created and is_correct and not obj.is_correct:
                        obj.is_correct = True
                        obj.save(update_fields=["is_correct"])

                    if is_correct and first_starred_text is None:
                        first_starred_text = text

                if first_starred_text:
                    Answer.objects.filter(question=question).exclude(
                        text=first_starred_text
                    ).update(is_correct=False)


# --- UserAnswer admin (tracking user submissions) ---
@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("visitor_id", "question", "is_correct")
    list_filter = ("is_correct", "question__quiz")
