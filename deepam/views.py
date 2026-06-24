from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Deepam, PanchangaSnapshot
from .services import lamp_state, panchangam_for_today


@login_required
def dashboard(request):
	if request.method == "POST":
		action = request.POST.get("action")
		if action == "delete_lamp":
			lamp = Deepam.objects.filter(id=request.POST.get("lamp_id"), user=request.user).first()
			if lamp is None:
				raise Http404("Lamp not found")
			PanchangaSnapshot.objects.filter(deepam=lamp).delete()
			lamp.delete()
			messages.success(request, "Lamp deleted successfully.")
			return redirect("dashboard")

	lamps = Deepam.objects.filter(user=request.user).order_by("-created_at")
	enriched_lamps = []
	for lamp in lamps:
		state = lamp_state(lamp)
		snapshot = getattr(lamp, "panchangasnapshot", None)
		enriched_lamps.append(
			{
				"lamp": lamp,
				"is_lit": state["is_lit"],
				"state_label": state["state_label"],
				"next_event_label": state["next_event_label"],
				"next_event_display": state["next_event_display"],
				"remaining": state["remaining"],
				"remaining_display": state["remaining_display"],
				"snapshot": snapshot,
			}
		)

	context = {
		"active_lamps_count": lamps.filter(active=True).count(),
		"lamps": enriched_lamps,
		"today_panchangam": panchangam_for_today(timezone.now().date()),
	}
	return render(request, "deepam/dashboard.html", context)
@login_required
def lamp_detail(request, lamp_id):
    lamp = Deepam.objects.filter(
        id=lamp_id,
        user=request.user
    ).first()

    if lamp is None:
        raise Http404("Lamp not found")

    state = lamp_state(lamp)

    context = {
        "lamp": lamp,
        "snapshot": getattr(lamp, "panchangasnapshot", None),
        "state": state,
    }

    return render(
        request,
        "deepam/lamp_detail.html",
        context,
    )