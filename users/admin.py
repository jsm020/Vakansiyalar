from django.contrib import admin
from .models import User, Diploma, Passport, Requirement, UserRequirement, UserRequirementScore
from django import forms

class UserRequirementScoreForm(forms.ModelForm):
    class Meta:
        model = UserRequirementScore
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter requirements by selected user_requirement
        if "user_requirement" in self.data:
            try:
                ur_id = int(self.data.get("user_requirement"))
                ur = UserRequirement.objects.get(pk=ur_id)
                self.fields["requirement"].queryset = ur.requirements.all()
            except (ValueError, UserRequirement.DoesNotExist):
                self.fields["requirement"].queryset = self.fields["requirement"].queryset.none()
        elif self.instance.pk and self.instance.user_requirement:
            ur = self.instance.user_requirement
            self.fields["requirement"].queryset = ur.requirements.all()

        # Set controller field to requirement.controller
        if "requirement" in self.data:
            try:
                req_id = int(self.data.get("requirement"))
                from .models import Requirement
                req = Requirement.objects.get(pk=req_id)
                self.fields["controller"].initial = req.controller
            except (ValueError, Requirement.DoesNotExist):
                self.fields["controller"].initial = None
        elif self.instance.pk and self.instance.requirement:
            req = self.instance.requirement
            self.fields["controller"].initial = req.controller

class RequirementAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['controller'].queryset = User.objects.filter(is_superuser=True)

    class Meta:
        model = Requirement
        fields = '__all__'

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    form = RequirementAdminForm
    list_display = ("id", "title", "max_score", "controller", "created_at")
    search_fields = ("title", "controller__username")
    list_filter = ("controller",)

@admin.register(UserRequirement)
class UserRequirementAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "score", "created_at")
    filter_horizontal = ("requirements",)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "middle_name", "phone", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "first_name", "last_name", "phone")
    list_filter = ("is_active", "is_staff", "date_joined")


@admin.register(Diploma)
class DiplomaAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "specialization", "graduation_year", "diploma_number", "created_at")
    search_fields = ("user__username", "specialization", "diploma_number")
    list_filter = ("graduation_year", "specialization")


@admin.register(Passport)
class PassportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "passport_seriya", "passport_number", "passport_jshir", "cv_file", "created_at")
    search_fields = ("user__username", "passport_seriya", "passport_number", "passport_jshir")
    list_filter = ("passport_seriya",)


@admin.register(UserRequirementScore)
class UserRequirementScoreAdmin(admin.ModelAdmin):
    form = UserRequirementScoreForm
    list_display = ("id", "user_requirement", "requirement", "score", "controller", "created_at")
    search_fields = ("user_requirement__user__username", "requirement__title", "controller__username")
    list_filter = ("controller", "requirement")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "requirement" and request.GET.get("user_requirement"):
            try:
                ur_id = request.GET.get("user_requirement")
                from .models import UserRequirement
                ur = UserRequirement.objects.get(pk=ur_id)
                kwargs["queryset"] = ur.requirements.all()
            except Exception:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
