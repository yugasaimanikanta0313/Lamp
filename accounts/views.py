from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import EmailLoginForm, OTPVerifyForm
from .models import EmailOTP
from .services import send_login_otp


def login_view(request):
	form = EmailLoginForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		email = form.cleaned_data["email"]
		send_login_otp(email)
		request.session["otp_email"] = email
		messages.success(request, "OTP sent to your email address.")
		return redirect("verify_otp")
	return render(request, "accounts/login.html", {"form": form})


def verify_otp_view(request):
	email = request.session.get("otp_email", "")
	form = OTPVerifyForm(request.POST or None)
	if request.method == "POST" and form.is_valid() and email:
		typed_otp = form.cleaned_data["otp"]
		otp_record = (
			EmailOTP.objects.filter(email=email, otp=typed_otp, is_verified=False)
			.order_by("-created_at")
			.first()
		)
		if otp_record and not otp_record.is_expired():
			otp_record.is_verified = True
			otp_record.save(update_fields=["is_verified"])
			User = get_user_model()
			username = email.split("@", 1)[0]
			user, _ = User.objects.get_or_create(email=email, defaults={"username": username})
			if not user.username:
				user.username = username
				user.save(update_fields=["username"])
			login(request, user)
			request.session.pop("otp_email", None)
			messages.success(request, "OTP verified successfully.")
			return redirect("dashboard")
		messages.error(request, "Invalid or expired OTP.")
	return render(request, "accounts/verify_otp.html", {"email": email, "form": form})


@login_required
def profile_view(request):
	from deepam.forms import DeepamForm, ProfileForm
	from deepam.models import Deepam, PanchangaSnapshot
	from panchangam.utils import get_panchangam

	profile_instance = request.user if request.user.is_authenticated else None
	profile_form = ProfileForm(request.POST or None, instance=profile_instance, prefix="profile") if profile_instance else None
	edit_lamp_id = request.GET.get("lamp_id")
	edit_lamp = None
	edit_lamp_form = None
	if edit_lamp_id:
		edit_lamp = Deepam.objects.filter(id=edit_lamp_id, user=request.user).first()
		if edit_lamp is None:
			raise Http404("Lamp not found")
		edit_lamp_form = DeepamForm(
			initial={
				"title": edit_lamp.title,
				"start_date": edit_lamp.start_time.date(),
				"start_hour": edit_lamp.start_time.strftime("%I"),
				"start_minute": edit_lamp.start_time.strftime("%M"),
				"start_period": edit_lamp.start_time.strftime("%p"),
				"end_date": edit_lamp.end_time.date(),
				"end_hour": edit_lamp.end_time.strftime("%I"),
				"end_minute": edit_lamp.end_time.strftime("%M"),
				"end_period": edit_lamp.end_time.strftime("%p"),
			},
			prefix="edit_lamp",
		)
	lamp_form = DeepamForm(request.POST or None, prefix="lamp")
	user_lamps = Deepam.objects.filter(user=request.user).order_by("-created_at") if request.user.is_authenticated else []

	if request.method == "POST" and request.user.is_authenticated:
		action = request.POST.get("action")
		if action == "save_profile" and profile_form and profile_form.is_valid():
			profile_form.save()
			messages.success(request, "Profile updated successfully.")
			return redirect("profile")
		if action == "create_lamp" and lamp_form.is_valid():
			lamp = Deepam.objects.create(
				user=request.user,
				title=lamp_form.cleaned_data["title"],
				start_time=lamp_form.cleaned_data["start_datetime"],
				end_time=lamp_form.cleaned_data["end_datetime"],
				active=True,
			)
			snapshot = get_panchangam(lamp.start_time.date())
			PanchangaSnapshot.objects.create(deepam=lamp, **snapshot)
			messages.success(request, "Lamp created successfully.")
			return redirect("profile")
		if action == "update_lamp":
			lamp = Deepam.objects.filter(id=request.POST.get("lamp_id"), user=request.user).first()
			if lamp is None:
				raise Http404("Lamp not found")
			edit_form = DeepamForm(request.POST, prefix="edit_lamp")
			edit_lamp = lamp
			edit_lamp_form = edit_form
			if edit_form.is_valid():
				lamp.title = edit_form.cleaned_data["title"]
				lamp.start_time = edit_form.cleaned_data["start_datetime"]
				lamp.end_time = edit_form.cleaned_data["end_datetime"]
				lamp.save(update_fields=["title", "start_time", "end_time"])
				snapshot_data = get_panchangam(lamp.start_time.date())
				PanchangaSnapshot.objects.update_or_create(
					deepam=lamp,
					defaults=snapshot_data,
				)
				messages.success(request, "Lamp updated successfully.")
				return redirect("profile")
		if action == "delete_lamp":
			lamp = Deepam.objects.filter(id=request.POST.get("lamp_id"), user=request.user).first()
			if lamp is None:
				raise Http404("Lamp not found")
			lamp.delete()
			messages.success(request, "Lamp deleted successfully.")
			return redirect("profile")

	return render(
		request,
		"accounts/profile.html",
		{
			"profile_form": profile_form,
			"lamp_form": lamp_form,
			"edit_lamp_form": edit_lamp_form,
			"edit_lamp": edit_lamp,
			"user_lamps": user_lamps,
		},
	)
