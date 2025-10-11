/**
 * Festival Admin JavaScript
 * Enhanced functionality for Persian admin interface
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-load cities when province changes
    const provinceSelect = document.querySelector('#id_province');
    const citySelect = document.querySelector('#id_city');
    
    if (provinceSelect && citySelect) {
        provinceSelect.addEventListener('change', function() {
            const provinceId = this.value;
            
            if (provinceId) {
                loadCities(provinceId);
            } else {
                clearCities();
            }
        });
    }
    
    /**
     * Load cities for selected province
     */
    function loadCities(provinceId) {
        const url = '/admin/festival/festivalregistration/ajax/load-cities/';
        
        fetch(`${url}?province_id=${provinceId}`)
            .then(response => response.json())
            .then(data => {
                clearCities();
                
                // Add default option
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = 'شهر را انتخاب کنید';
                citySelect.appendChild(defaultOption);
                
                // Add cities
                data.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city.id;
                    option.textContent = city.name;
                    citySelect.appendChild(option);
                });
                
                citySelect.disabled = false;
            })
            .catch(error => {
                console.error('Error loading cities:', error);
                clearCities();
            });
    }
    
    /**
     * Clear city options
     */
    function clearCities() {
        citySelect.innerHTML = '<option value="">در حال بارگذاری...</option>';
        citySelect.disabled = true;
    }
    
    // National ID validation
    const nationalIdInput = document.querySelector('#id_national_id');
    if (nationalIdInput) {
        nationalIdInput.addEventListener('blur', function() {
            validateNationalId(this.value);
        });
        
        nationalIdInput.addEventListener('input', function() {
            // Only allow digits
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // Limit to 10 digits
            if (this.value.length > 10) {
                this.value = this.value.slice(0, 10);
            }
        });
    }
    
    /**
     * Validate Iranian National ID
     */
    function validateNationalId(nationalId) {
        if (!nationalId || nationalId.length !== 10) {
            return false;
        }
        
        // Check for invalid patterns
        const invalidPatterns = [
            '0000000000', '1111111111', '2222222222', '3333333333',
            '4444444444', '5555555555', '6666666666', '7777777777',
            '8888888888', '9999999999'
        ];
        
        if (invalidPatterns.includes(nationalId)) {
            showValidationError(nationalIdInput, 'کد ملی معتبر نیست');
            return false;
        }
        
        // Calculate checksum
        let sum = 0;
        for (let i = 0; i < 9; i++) {
            sum += parseInt(nationalId[i]) * (10 - i);
        }
        
        const remainder = sum % 11;
        const checkDigit = parseInt(nationalId[9]);
        
        const isValid = (remainder < 2 && checkDigit === remainder) || 
                       (remainder >= 2 && checkDigit === 11 - remainder);
        
        if (!isValid) {
            showValidationError(nationalIdInput, 'کد ملی معتبر نیست');
            return false;
        }
        
        clearValidationError(nationalIdInput);
        return true;
    }
    
    // Phone number validation
    const phoneInput = document.querySelector('#id_phone_number');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            // Only allow digits and common separators
            this.value = this.value.replace(/[^0-9\-]/g, '');
            
            // Format as 09XX-XXX-XXXX
            if (this.value.length >= 11 && this.value.startsWith('09')) {
                const formatted = this.value.replace(/(\d{4})(\d{3})(\d{4})/, '$1-$2-$3');
                this.value = formatted;
            }
        });
        
        phoneInput.addEventListener('blur', function() {
            validatePhoneNumber(this.value);
        });
    }
    
    /**
     * Validate Iranian mobile number
     */
    function validatePhoneNumber(phoneNumber) {
        const cleanPhone = phoneNumber.replace(/[\-\s]/g, '');
        
        if (!cleanPhone.startsWith('09') || cleanPhone.length !== 11) {
            showValidationError(phoneInput, 'شماره موبایل باید با 09 شروع شده و 11 رقمی باشد');
            return false;
        }
        
        clearValidationError(phoneInput);
        return true;
    }
    
    /**
     * Show validation error
     */
    function showValidationError(input, message) {
        clearValidationError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'validation-error';
        errorDiv.style.color = '#dc3545';
        errorDiv.style.fontSize = '12px';
        errorDiv.style.marginTop = '5px';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
        input.style.borderColor = '#dc3545';
    }
    
    /**
     * Clear validation error
     */
    function clearValidationError(input) {
        const existingError = input.parentNode.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }
        input.style.borderColor = '';
    }
    
    // Festival statistics loading
    const statsButton = document.querySelector('#load-festival-stats');
    if (statsButton) {
        statsButton.addEventListener('click', function(e) {
            e.preventDefault();
            loadFestivalStatistics();
        });
    }
    
    /**
     * Load festival statistics
     */
    function loadFestivalStatistics() {
        const url = '/admin/festival/festivalregistration/statistics/';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                displayStatistics(data);
            })
            .catch(error => {
                console.error('Error loading statistics:', error);
            });
    }
    
    /**
     * Display statistics
     */
    function displayStatistics(stats) {
        const container = document.querySelector('#statistics-container');
        if (!container) return;
        
        let html = '<div class="festival-stats">';
        html += '<h3>📊 آمار جشنواره</h3>';
        
        html += `<div class="stat-item">
            <span class="stat-number">${stats.total_registrations}</span>
            <span class="stat-label">کل ثبت نام‌ها</span>
        </div>`;
        
        // Format statistics
        if (stats.by_format) {
            html += '<h4>🎬 آمار قالب‌ها</h4>';
            Object.entries(stats.by_format).forEach(([format, count]) => {
                html += `<div class="stat-item">
                    <span class="stat-number">${count}</span>
                    <span class="stat-label">${format}</span>
                </div>`;
            });
        }
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    // Auto-save functionality
    let autoSaveTimeout;
    const formInputs = document.querySelectorAll('input, select, textarea');
    
    formInputs.forEach(input => {
        if (input.type !== 'submit' && input.type !== 'button') {
            input.addEventListener('input', function() {
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(() => {
                    showAutoSaveIndicator();
                }, 2000);
            });
        }
    });
    
    /**
     * Show auto-save indicator
     */
    function showAutoSaveIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator';
        indicator.textContent = '💾 در حال ذخیره خودکار...';
        indicator.style.position = 'fixed';
        indicator.style.top = '10px';
        indicator.style.right = '10px';
        indicator.style.background = '#28a745';
        indicator.style.color = 'white';
        indicator.style.padding = '8px 12px';
        indicator.style.borderRadius = '5px';
        indicator.style.zIndex = '9999';
        indicator.style.fontSize = '12px';
        
        document.body.appendChild(indicator);
        
        setTimeout(() => {
            indicator.remove();
        }, 2000);
    }
    
    // Enhanced form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                showFormErrors();
            }
        });
    }
    
    /**
     * Validate entire form
     */
    function validateForm() {
        let isValid = true;
        
        // Validate national ID
        if (nationalIdInput && !validateNationalId(nationalIdInput.value)) {
            isValid = false;
        }
        
        // Validate phone number
        if (phoneInput && !validatePhoneNumber(phoneInput.value)) {
            isValid = false;
        }
        
        return isValid;
    }
    
    /**
     * Show form validation errors
     */
    function showFormErrors() {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-errors';
        errorDiv.innerHTML = `
            <div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0;">
                ⚠️ لطفاً خطاهای فرم را بررسی و اصلاح کنید
            </div>
        `;
        
        const submitRow = document.querySelector('.submit-row');
        if (submitRow) {
            submitRow.parentNode.insertBefore(errorDiv, submitRow);
            
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }
    }
    
    // Print functionality
    const printButton = document.querySelector('#print-registration');
    if (printButton) {
        printButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    }
    
    console.log('Festival Admin JavaScript loaded successfully ✅');
});