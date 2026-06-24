from django import forms


class EmailLoginForm(forms.Form):
	email = forms.EmailField(
		label="Email address",
		widget=forms.EmailInput(
			attrs={
				"placeholder": "name@example.com",
				"autocomplete": "email",
			}
		),
	)


class OTPVerifyForm(forms.Form):
	otp = forms.CharField(
		label="OTP",
		min_length=6,
		max_length=6,
		widget=forms.TextInput(
			attrs={
				"placeholder": "Enter 6-digit OTP",
				"inputmode": "numeric",
				"autocomplete": "one-time-code",
			}
		),
	)
