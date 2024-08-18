function submitForm(formId) {
    document.getElementById(formId).submit();
}


const select = document.getElementById('fumehood');
            const customInput = document.getElementById('custom_fumehood');
            
            // Store the original options in an array
            const originalOptions = Array.from(select.options).map(option => option.value);
        
            customInput.addEventListener('input', () => {
                const customValue = customInput.value;
                select.innerHTML = '';
        
                if (customValue) {
                    // Filter the original options based on user input
                    const filteredOptions = originalOptions.filter(option => option.includes(customValue));
                    
                    // If there are suggestions, add them to the select
                    if (filteredOptions.length > 0) {
                        filteredOptions.forEach(optionValue => {
                            const option = document.createElement('option');
                            option.value = optionValue;
                            option.text = optionValue;
                            select.appendChild(option);
                        });
                    } else {
                        // If there are no suggestions, provide a message or default option
                        const option = document.createElement('option');
                        option.value = '';
                        option.text = 'No matching suggestions';
                        select.appendChild(option);
                    }
                } else {
                    // Restore the original options if input is empty
                    originalOptions.forEach(optionValue => {
                        const option = document.createElement('option');
                        option.value = optionValue;
                        option.text = optionValue;
                        select.appendChild(option);
                    });
                }
            });


// Calculate the default values for start date and end date
const tdyDay = new Date();
const lastDay = new Date()
lastDay.setDate(tdyDay.getDate() - 1)
const oneWeekBeforeLastDay = new Date();
oneWeekBeforeLastDay.setDate(lastDay.getDate() - 7);

// Format the default dates as yyyy-MM-dd
const defaultStartDate = oneWeekBeforeLastDay.toISOString().split('T')[0];
const defaultEndDate = lastDay.toISOString().split('T')[0];

// Set the default values for the date input fields
document.getElementById('start_date').value = defaultStartDate;
document.getElementById('end_date').value = defaultEndDate;