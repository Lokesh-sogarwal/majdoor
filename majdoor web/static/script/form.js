const stepMenus = document.querySelectorAll('.formbold-step-menu1, .formbold-step-menu2, .formbold-step-menu3');
const steps = document.querySelectorAll('.formbold-form-step-1, .formbold-form-step-2, .formbold-form-step-3');

const formSubmitBtn = document.querySelector('.formbold-btn');
const formBackBtn = document.querySelector('.formbold-back-btn');
const dob = document.getElementById("dob");

let currentStep = 0; // Track the current step (0, 1, 2)

// Function to toggle steps
function toggleSteps(fromIndex, toIndex) {
  stepMenus[fromIndex].classList.remove('active');
  stepMenus[toIndex].classList.add('active');

  steps[fromIndex].classList.remove('active');
  steps[toIndex].classList.add('active');
}

// Validate fields in the current step
function validateStep(stepIndex) {
  const inputs = steps[stepIndex].querySelectorAll(".formbold-form-input");
  let isValid = true;

  inputs.forEach(input => {
    if (!input.value.trim()) {
      isValid = false;
      input.style.borderColor = "red";
    } else {
      input.style.borderColor = "";
    }
  });

  if (!isValid) {
    alert("Please fill all required fields.");
  }
  return isValid;
}

// Handle next/submit button
formSubmitBtn.addEventListener("click", function (event) {
  event.preventDefault();

  // Validate the current step before moving forward
  if (!validateStep(currentStep)) return;

  if (currentStep < steps.length - 1) {
    toggleSteps(currentStep, currentStep + 1);
    currentStep++;

    if (currentStep === steps.length - 1) {
      formSubmitBtn.textContent = "Submit";
    }
    formBackBtn.classList.add('active');
  } else {
    document.querySelector("form").submit();
  }
});

// Handle back button
formBackBtn.addEventListener("click", function (event) {
  event.preventDefault();

  if (currentStep > 0) {
    toggleSteps(currentStep, currentStep - 1);
    currentStep--;

    formSubmitBtn.textContent = "Next";
    if (currentStep === 0) {
      formBackBtn.classList.remove('active');
    }
  }
});

// Validate date of booking
dob.addEventListener("change", function () {
  const selectedDate = new Date(dob.value);
  const today = new Date();
  if (selectedDate < today) {
    alert("Booking date cannot be in the past.");
    dob.value = "";
  }
});
