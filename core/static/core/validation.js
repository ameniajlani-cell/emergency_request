(function () {
    const rules = {
        name: [
            {
                test: (value) => value.length >= 2,
                message: 'Name must contain at least 2 characters.',
            },
            {
                test: (value) => /^[\p{L}\s'-]+$/u.test(value),
                message: 'Name can contain only letters, spaces, apostrophes, and hyphens.',
            },
        ],
        phone: [
            {
                test: (value) => {
                    const digits = value.replace(/\D/g, '');
                    return /^\+?[0-9\s().-]{8,20}$/.test(value) && digits.length >= 8;
                },
                message: 'Enter a valid phone number between 8 and 20 characters.',
            },
        ],
        location: [
            {
                test: (value) => value.length >= 3,
                message: 'Location must contain at least 3 characters.',
            },
        ],
        title: [
            {
                test: (value) => value.length >= 3,
                message: 'Title must contain at least 3 characters.',
            },
        ],
        description: [
            {
                test: (value) => value.length >= 10,
                message: 'Description must contain at least 10 characters.',
            },
        ],
        emergency_type: [
            {
                test: (value) => value.length > 0,
                message: 'Choose a valid emergency type.',
            },
        ],
        status: [
            {
                test: (value) => ['pending', 'in_progress', 'resolved'].includes(value),
                message: 'Choose a valid status.',
            },
        ],
    };

    function getErrorElement(field) {
        const id = `${field.id || field.name}-client-error`;
        let error = document.getElementById(id);

        if (!error) {
            error = document.createElement('div');
            error.id = id;
            error.className = 'client-error';
            field.insertAdjacentElement('afterend', error);
        }

        return error;
    }

    function clearError(field) {
        const error = document.getElementById(`${field.id || field.name}-client-error`);

        field.removeAttribute('aria-invalid');
        field.classList.remove('is-invalid');

        if (error) {
            error.textContent = '';
        }
    }

    function showError(field, message) {
        const error = getErrorElement(field);

        field.setAttribute('aria-invalid', 'true');
        field.classList.add('is-invalid');
        error.textContent = message;
    }

    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name.includes('-') ? field.name.split('-').pop() : field.name;
        const fieldRules = rules[fieldName];

        if (!fieldRules) {
            return true;
        }

        if (!value) {
            showError(field, 'This field is required.');
            return false;
        }

        for (const rule of fieldRules) {
            if (!rule.test(value)) {
                showError(field, rule.message);
                return false;
            }
        }

        clearError(field);
        return true;
    }

    document.querySelectorAll('form[data-validate="emergency"]').forEach((form) => {
        form.setAttribute('novalidate', 'novalidate');

        const fields = Array.from(form.querySelectorAll('input, textarea, select'));

        fields.forEach((field) => {
            field.addEventListener('blur', () => validateField(field));
            field.addEventListener('input', () => {
                if (field.getAttribute('aria-invalid') === 'true') {
                    validateField(field);
                }
            });
        });

        form.addEventListener('submit', (event) => {
            const results = fields.map((field) => validateField(field));

            if (results.includes(false)) {
                event.preventDefault();
                fields.find((field) => field.getAttribute('aria-invalid') === 'true').focus();
            }
        });
    });
}());
