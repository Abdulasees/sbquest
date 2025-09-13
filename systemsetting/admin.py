from django import forms
from django.contrib import admin
import nested_admin
from .models import DailyOffer, DailyOfferQuestion, DailyOfferAnswer


# --- Form: adds a textarea field to Question inline ---
class BulkAnswerForm(forms.ModelForm):
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
        model = DailyOfferQuestion
        fields = "__all__"


# --- Answers inline (normal per-row edit still works) ---
class DailyOfferAnswerInline(nested_admin.NestedTabularInline):
    model = DailyOfferAnswer
    extra = 0
    fields = ("answer_text", "answer_image", "is_correct")


# --- Questions inline (shows the bulk textarea) ---
class DailyOfferQuestionInline(nested_admin.NestedStackedInline):
    model = DailyOfferQuestion
    form = BulkAnswerForm
    extra = 1
    inlines = [DailyOfferAnswerInline]


@admin.register(DailyOffer)
class DailyOfferAdmin(nested_admin.NestedModelAdmin):
    inlines = [DailyOfferQuestionInline]
    exclude = ("description",)

    def save_formset(self, request, form, formset, change):
        """
        Save all inlines first so questions have PKs, then process bulk_answers
        for the DailyOfferQuestion inline forms.
        """
        super().save_formset(request, form, formset, change)

        # Only handle the Question inline's formset
        if getattr(formset, "model", None) is DailyOfferQuestion:
            for q_form in formset.forms:
                cd = getattr(q_form, "cleaned_data", None)
                if not cd:
                    continue

                bulk_text = (cd.get("bulk_answers") or "").strip()
                if not bulk_text:
                    continue

                question = q_form.instance  # saved question object with PK

                lines = [ln.strip() for ln in bulk_text.splitlines() if ln.strip()]
                first_starred_text = None

                for line in lines:
                    is_correct = line.startswith("*")
                    text = line[1:].strip() if is_correct else line

                    # Avoid duplicates: only create if not exists
                    obj, created = DailyOfferAnswer.objects.get_or_create(
                        question=question,
                        answer_text=text,
                        defaults={"is_correct": is_correct},
                    )

                    if created:
                        # If newly created and marked correct
                        if is_correct:
                            obj.is_correct = True
                            obj.save(update_fields=["is_correct"])
                    else:
                        # If existing and should be correct, update
                        if is_correct and not obj.is_correct:
                            obj.is_correct = True
                            obj.save(update_fields=["is_correct"])

                    # Remember the first starred line to enforce "only one correct"
                    if is_correct and first_starred_text is None:
                        first_starred_text = text

                # Enforce only one correct answer if starred given
                if first_starred_text:
                    DailyOfferAnswer.objects.filter(question=question).exclude(
                        answer_text=first_starred_text
                    ).update(is_correct=False)
