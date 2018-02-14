/**
 * Created by colinwren on 30/08/15.
 */
describe('Data Entry Functionality', function(){
    beforeEach(function(){
        var bodyEl = document.getElementsByTagName('body')[0];
        var test = document.getElementById('test');
        if (test != null) {
            test.parentNode.removeChild(test);
        }
        var testArea = document.createElement('div');
        testArea.setAttribute('id', 'test');
        testArea.style.height = '500px';
        testArea.innerHTML = '';
        bodyEl.appendChild(testArea);
    });

    afterEach(function(){
       cleanUp();
    });

    it('Has functionality to handle forms', function(){
       expect(typeof(NHMobileForm.prototype)).toBe('object');
    });



    describe('Form Validation', function() {

        afterEach(function () {
            cleanUp();
        });

        it('Has functionality to validate a form', function(){
           expect(typeof(NHMobileForm.prototype.validate)).toBe('function');
        });

        it('Has functionality to reset input errors so we can correct invalid inputs', function(){
           expect(typeof(NHMobileForm.prototype.reset_input_errors)).toBe('function');
        });

        it('Has functionality to add input errors so we can flag up invalid inputs', function(){
           expect(typeof(NHMobileForm.prototype.add_input_errors)).toBe('function');
        });

        describe('Validation on a number input', function(){
             var mobile;
             beforeEach(function(){
                 spyOn(NHMobileForm.prototype, 'submit');
                 spyOn(NHMobileForm.prototype, 'handle_timeout');
                 spyOn(NHMobileForm.prototype, 'validate').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'reset_input_errors').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'add_input_errors').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                     var promise = new Promise();
                     var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                     return promise;
                 });

                 var test = document.getElementById('test');
                 test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                     '<div class="block obsField" id="parent_test_int">' +
                     '<div class="input-header">' +
                     '<label for="test_int">Test Integer</label>' +
                     '<input type="number" name="test_int" id="test_int" min="10" max="20" step="1" data-required="false" data-necessary="true">' +
                     '</div>' +
                     '<div class="input-body">' +
                     '<span class="errors"></span>' +
                     '<span class="help"></span>' +
                     '</div>' +
                     '</div>' +
                     '<div class="block obsField" id="parent_test_float">' +
                     '<div class="input-header">' +
                     '<label for="test_float">Test Float</label>' +
                     '<input type="number" name="test_float" id="test_float" min="10" max="20" step="0.1" data-required="false" data-necessary="true">' +
                     '</div>' +
                     '<div class="input-body">' +
                     '<span class="errors"></span>' +
                     '<span class="help"></span>' +
                     '</div>' +
                     '</div>' +
                     '<div class="block obsField" id="parent_test_attr">' +
                     '<div class="input-header">' +
                     '<label for="test_attr">Test Attribute</label>' +
                     '<input type="number" name="test_attr" id="test_attr" min="10" max="20" step="1" data-validation="[{\'message\': {\'target\': \'target error\', \'value\': \'value error\'}, \'condition\': {\'operator\': \'<\', \'target\': \'test_attr\', \'value\': \'test_int\'}}]" data-required="false" data-necessary="true">' +
                     '</div>' +
                     '<div class="input-body">' +
                     '<span class="errors"></span>' +
                     '<span class="help"></span>' +
                     '</div>' +
                     '</div>' +
                     '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                     '</form>';
                 mobile = new NHMobileForm();
             });

            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            it('Informs the user when they set the input to a value lower than the min specified', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testInt = document.getElementById('test_int');
                var parentInt = testInt.parentNode.parentNode;
                var testFloat = document.getElementById('test_float');
                var parentFloat = testFloat.parentNode.parentNode;
                var intErrors = parentInt.getElementsByClassName('errors')[0];
                var floatErrors = parentFloat.getElementsByClassName('errors')[0];

                // set value
                testInt.value = 0;
                testFloat.value = 0;

                // change event - int
                var intEvent = document.createEvent('CustomEvent');
                intEvent.initCustomEvent('change', false, true, false);
                testInt.dispatchEvent(intEvent);

                // verify calls - int
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - int
                expect(parentInt.classList.contains('error')).toBe(true);
                expect(intErrors.innerHTML).toBe('<label for="test_int" class="error">Input too low</label>');

                // change event - float
                var floatEvent = document.createEvent('CustomEvent');
                floatEvent.initCustomEvent('change', false, true, false);
                testFloat.dispatchEvent(floatEvent);

                // verify calls - float
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - float
                expect(parentFloat.classList.contains('error')).toBe(true);
                expect(floatErrors.innerHTML).toBe('<label for="test_float" class="error">Input too low</label>');
            });

            it('Informs the user when they set the input to a value higher than the max specified', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testInt = document.getElementById('test_int');
                var parentInt = testInt.parentNode.parentNode;
                var testFloat = document.getElementById('test_float');
                var parentFloat = testFloat.parentNode.parentNode;
                var intErrors = parentInt.getElementsByClassName('errors')[0];
                var floatErrors = parentFloat.getElementsByClassName('errors')[0];

                // set value
                testInt.value = 1337;
                testFloat.value = 1337;

                // change event - int
                var intEvent = document.createEvent('CustomEvent');
                intEvent.initCustomEvent('change', false, true, false);
                testInt.dispatchEvent(intEvent);

                // verify calls - int
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - int
                expect(parentInt.classList.contains('error')).toBe(true);
                expect(intErrors.innerHTML).toBe('<label for="test_int" class="error">Input too high</label>');

                // change event - float
                var floatEvent = document.createEvent('CustomEvent');
                floatEvent.initCustomEvent('change', false, true, false);
                testFloat.dispatchEvent(floatEvent);

                // verify calls - float
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - float
                expect(parentFloat.classList.contains('error')).toBe(true);
                expect(floatErrors.innerHTML).toBe('<label for="test_float" class="error">Input too high</label>');
            });

            it('Informs the user when they set the input to a float value and the input is a integer', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testInt = document.getElementById('test_int');
                var parentInt = testInt.parentNode.parentNode;
                var testFloat = document.getElementById('test_float');
                var parentFloat = testFloat.parentNode.parentNode;
                var intErrors = parentInt.getElementsByClassName('errors')[0];
                var floatErrors = parentFloat.getElementsByClassName('errors')[0];

                // set value
                testInt.value = 11.5;
                testFloat.value = 11.5;

                // change event - int
                var intEvent = document.createEvent('CustomEvent');
                intEvent.initCustomEvent('change', false, true, false);
                testInt.dispatchEvent(intEvent);

                // verify calls - int
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - int
                expect(parentInt.classList.contains('error')).toBe(true);
                expect(intErrors.innerHTML).toBe('<label for="test_int" class="error">Must be whole number</label>');

                // change event - float
                var floatEvent = document.createEvent('CustomEvent');
                floatEvent.initCustomEvent('change', false, true, false);
                testFloat.dispatchEvent(floatEvent);

                // verify calls - float
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - float
                expect(parentFloat.classList.contains('error')).toBe(false);
                expect(floatErrors.innerHTML).toBe('');
            });

            it('Informs the user when they set the input to a value that does not meet the criteria of the data-validation attribute', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testInt = document.getElementById('test_int');
                var parentInt = testInt.parentNode.parentNode;
                var testAttr = document.getElementById('test_attr');
                var parentAttr = testAttr.parentNode.parentNode;
                var intErrors = parentInt.getElementsByClassName('errors')[0];
                var attrErrors = parentAttr.getElementsByClassName('errors')[0];

                // set value
                testInt.value = 11;
                testAttr.value = 18;

                // change event
                var attrEvent = document.createEvent('CustomEvent');
                attrEvent.initCustomEvent('change', false, true, false);
                testAttr.dispatchEvent(attrEvent);

                // verify calls
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM
                expect(parentAttr.classList.contains('error')).toBe(true);
                expect(attrErrors.innerHTML).toBe('<label for="test_attr" class="error">target error</label>');
                expect(parentInt.classList.contains('error')).toBe(true);
                expect(intErrors.innerHTML).toBe('<label for="test_int" class="error">value error</label>');
            });

            it('Informs the user when they set the input to a value but the other input in data-validation is not set', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testInt = document.getElementById('test_int');
                var parentInt = testInt.parentNode.parentNode;
                var testAttr = document.getElementById('test_attr');
                var parentAttr = testAttr.parentNode.parentNode;
                var intErrors = parentInt.getElementsByClassName('errors')[0];
                var attrErrors = parentAttr.getElementsByClassName('errors')[0];

                // set value
                testAttr.value = 18;

                // change event
                var attrEvent = document.createEvent('CustomEvent');
                attrEvent.initCustomEvent('change', false, true, false);
                testAttr.dispatchEvent(attrEvent);

                // verify calls
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM
                expect(parentAttr.classList.contains('error')).toBe(true);
                expect(attrErrors.innerHTML).toBe('<label for="test_attr" class="error">target error</label>');
                expect(parentInt.classList.contains('error')).toBe(true);
                expect(intErrors.innerHTML).toBe('<label for="test_int" class="error">Please enter a value</label>');

                // Fix the issue
                NHMobileForm.prototype.add_input_errors.calls.reset();
                NHMobileForm.prototype.reset_input_errors.calls.reset();
                NHMobileForm.prototype.validate.calls.reset();
                testInt.value = 19;


                // change event
                var fixIntEvent = document.createEvent('CustomEvent');
                fixIntEvent.initCustomEvent('change', false, true, false);
                testInt.dispatchEvent(fixIntEvent);

                // change event
                var fixEvent = document.createEvent('CustomEvent');
                fixEvent.initCustomEvent('change', false, true, false);
                testAttr.dispatchEvent(fixEvent);

                // verify calls
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).not.toHaveBeenCalled();

                // verify DOM
                expect(parentAttr.classList.contains('error')).toBe(false);
                expect(attrErrors.innerHTML).toBe('');
                expect(parentInt.classList.contains('error')).toBe(false);
                expect(intErrors.innerHTML).toBe('');
            });

            it('Keeps invalid number flag when another validation criteria is met', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testInt = document.getElementById('test_int');
                var parentInt = testInt.parentNode.parentNode;
                var testAttr = document.getElementById('test_attr');
                var parentAttr = testAttr.parentNode.parentNode;
                var intErrors = parentInt.getElementsByClassName('errors')[0];
                var attrErrors = parentAttr.getElementsByClassName('errors')[0];

                // set value to be too low on the data-validation element
                testInt.value = 1337;

                // change event - attr
                var intHighEvent = document.createEvent('CustomEvent');
                intHighEvent.initCustomEvent('change', false, true, false);
                testInt.dispatchEvent(intHighEvent);

                // verify calls - attr
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - int
                expect(parentInt.classList.contains('error')).toBe(true);
                expect(intErrors.innerHTML).toBe('<label for="test_int" class="error">Input too high</label>');

                // set value to be normal for the target element on data-validation
                testAttr.value = 18;

                // change event
                var attrValEvent = document.createEvent('CustomEvent');
                attrValEvent.initCustomEvent('change', false, true, false);
                testAttr.dispatchEvent(attrValEvent);

                // verify calls
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM
                expect(parentInt.classList.contains('error')).toBe(true);
                expect(intErrors.innerHTML).toBe('<label for="test_int" class="error">Input too high</label>');
            });
        });

        describe('Validation on a text input', function(){
             var mobile;
             beforeEach(function(){
                 spyOn(NHMobileForm.prototype, 'submit');
                 spyOn(NHMobileForm.prototype, 'handle_timeout');
                 spyOn(NHMobileForm.prototype, 'validate').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'reset_input_errors').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'add_input_errors').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                     var promise = new Promise();
                     var empty = new NHMobileData({
                         status: 'success',
                         title: '',
                         description: '',
                         data: {}
                     })
                     promise.complete(empty);
                     return promise;
                 });

                 var test = document.getElementById('test');
                 test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                     '<div class="block obsField" id="parent_test_text">' +
                     '<div class="input-header">' +
                     '<label for="test_text">Test Text</label>' +
                     '<input type="text" name="test_text" id="test_text" pattern="^[0-9]{4,6}$" data-required="false" data-necessary="true">' +
                     '</div>' +
                     '<div class="input-body">' +
                     '<span class="errors"></span>' +
                     '<span class="help"></span>' +
                     '</div>' +
                     '</div>' +
                     '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                     '</form>';
                 mobile = new NHMobileForm();
             });

            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            it('Informs the user when they set the input to a value incorrect (too little)', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testText = document.getElementById('test_text');
                var parentText = testText.parentNode.parentNode;
                var textErrors = parentText.getElementsByClassName('errors')[0];

                // set incorrect value
                testText.value = '666';

                // change event - incorrect
                var threeEvent = document.createEvent('CustomEvent');
                threeEvent.initCustomEvent('change', false, true, false);
                testText.dispatchEvent(threeEvent);

                // verify calls - incorrect
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - incorrect
                expect(parentText.classList.contains('error')).toBe(true);
                expect(textErrors.innerHTML).toBe('<label for="test_text" class="error">Invalid value</label>');

                // set correct value
                testText.value = '1337';

                // change event - correct
                var fourEvent = document.createEvent('CustomEvent');
                fourEvent.initCustomEvent('change', false, true, false);
                testText.dispatchEvent(fourEvent);

                // verify calls - correct
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();

                // verify DOM - correct
                expect(parentText.classList.contains('error')).toBe(false);
                expect(textErrors.innerHTML).toBe('');
            });

            it('Informs the user when they set the input to a value incorrect (too much)', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testText = document.getElementById('test_text');
                var parentText = testText.parentNode.parentNode;
                var textErrors = parentText.getElementsByClassName('errors')[0];

                // set incorrect value
                testText.value = '1337666';

                // change event - incorrect
                var sevenEvent = document.createEvent('CustomEvent');
                sevenEvent.initCustomEvent('change', false, true, false);
                testText.dispatchEvent(sevenEvent);

                // verify calls - incorrect
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - incorrect
                expect(parentText.classList.contains('error')).toBe(true);
                expect(textErrors.innerHTML).toBe('<label for="test_text" class="error">Invalid value</label>');

                // set correct value
                testText.value = '1337';

                // change event - correct
                var fourEvent = document.createEvent('CustomEvent');
                fourEvent.initCustomEvent('change', false, true, false);
                testText.dispatchEvent(fourEvent);

                // verify calls - correct
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();

                // verify DOM - correct
                expect(parentText.classList.contains('error')).toBe(false);
                expect(textErrors.innerHTML).toBe('');
            });

            it('Informs the user when they set the input to a value incorrect (wrong type)', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testText = document.getElementById('test_text');
                var parentText = testText.parentNode.parentNode;
                var textErrors = parentText.getElementsByClassName('errors')[0];

                // set incorrect value
                testText.value = '1234a';

                // change event - incorrect
                var alphaEvent = document.createEvent('CustomEvent');
                alphaEvent.initCustomEvent('change', false, true, false);
                testText.dispatchEvent(alphaEvent);

                // verify calls - incorrect
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - incorrect
                expect(parentText.classList.contains('error')).toBe(true);
                expect(textErrors.innerHTML).toBe('<label for="test_text" class="error">Invalid value</label>');

                // set correct value
                testText.value = '1337';

                // change event - correct
                var fourEvent = document.createEvent('CustomEvent');
                fourEvent.initCustomEvent('change', false, true, false);
                testText.dispatchEvent(fourEvent);

                // verify calls - correct
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();

                // verify DOM - correct
                expect(parentText.classList.contains('error')).toBe(false);
                expect(textErrors.innerHTML).toBe('');
            });
        });

        describe('Validation for mandatory fields', function(){
             var mobile;
             beforeEach(function(){
                 spyOn(NHMobileForm.prototype, 'submit');
                 spyOn(NHMobileForm.prototype, 'handle_timeout');
                 spyOn(NHMobileForm.prototype, 'validate').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'reset_input_errors').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'add_input_errors').and.callThrough();
                 spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                     var promise = new Promise();
                     var empty = new NHMobileData({
                         status: 'success',
                         title: '',
                         description: '',
                         data: {}
                     })
                     promise.complete(empty);
                     return promise;
                 });

                 var test = document.getElementById('test');
                 test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                     '<div class="block obsField" id="parent_test_text">' +
                     '<div class="input-header">' +
                     '<label for="test_text">Test Text</label>' +
                     '</div>' +
                     '<div class="input-body">' +
                     '<select name="test_select" id="test_select" data-required="true" data-necessary="true">' +
                     '<option value="">Please Select</option>' +
                     '<option value="correct">Correct Value</option>'+
                     '</select>'+
                     '<span class="errors"></span>' +
                     '<span class="help"></span>' +
                     '</div>' +
                     '</div>' +
                     '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                     '</form>';
                 mobile = new NHMobileForm();
             });

            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            it('Informs the user when try to submit a form with empty mandatory values', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testText = document.getElementById('test_select');
                var parentText = testText.parentNode.parentNode;
                var textErrors = parentText.getElementsByClassName('errors')[0];

                // set incorrect value
                testText.value = '';

                // change event - incorrect
                var threeEvent = document.createEvent('CustomEvent');
                threeEvent.initCustomEvent('change', false, true, false);
                testText.dispatchEvent(threeEvent);

                // verify calls - incorrect
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();
                expect(NHMobileForm.prototype.add_input_errors).toHaveBeenCalled();

                // verify DOM - incorrect
                expect(parentText.classList.contains('error')).toBe(true);
                expect(textErrors.innerHTML).toBe('<label for="test_select" class="error">Missing value</label>');

                // set correct value
                testText.value = 'correct';

                // change event - correct
                var fourEvent = document.createEvent('CustomEvent');
                fourEvent.initCustomEvent('change', false, true, false);
                testText.dispatchEvent(fourEvent);

                // verify calls - correct
                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();
                expect(NHMobileForm.prototype.reset_input_errors).toHaveBeenCalled();

                // verify DOM - correct
                expect(parentText.classList.contains('error')).toBe(false);
                expect(textErrors.innerHTML).toBe('');
            });
        });
    });

    describe('Form Timeout', function() {
        var mobile;
        beforeEach(function () {
            spyOn(NHMobileForm.prototype, 'submit');
            spyOn(NHMobileForm.prototype, 'handle_timeout').and.callThrough();
            spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                var promise = new Promise();
                 var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                return promise;
            });
            spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
            var test = document.getElementById('test');
            test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                '<input type="submit" value="Test Submit" id="submit">' +
                '<input type="reset" value="Test Reset" id="reset">' +
                '<input type="radio" value="test_radio" id="radio">' +
                '<button id="reference">Test Button</button>' +
                '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                '</form>';
            mobile = new NHMobileForm();
        });

        afterEach(function () {
            cleanUp();
            mobile = null;
        });

        it('Has functionality to handle a form timeout', function(){
           expect(typeof(NHMobileForm.prototype.handle_timeout)).toBe('function');
        });

        it('Has functionality to reset the form timeout so form is kept alive when entering data', function(){
           expect(typeof(NHMobileForm.prototype.reset_form_timeout)).toBe('function');
        });

        it('Returns the task back to the server and informs the user that the form timed out', function(){
            var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
            var changeEvent = document.createEvent('CustomEvent', {
                'detail': 'form timed out'
            });
            changeEvent.initCustomEvent('form_timeout', false, true, false);
            document.dispatchEvent(changeEvent);
            expect(NHMobileForm.prototype.handle_timeout).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('form_timeout');
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Task window expired');
            expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Please pick the task again from the task list if you wish to complete it</p>');
        });
    });

    describe('Form Submission', function() {
        beforeEach(function () {

        });

        afterEach(function () {
            cleanUp();
        });
        it('Has functionality to submit a form', function(){
           expect(typeof(NHMobileForm.prototype.submit)).toBe('function');
        });

        it('Has functionality to display partial reasons if a form is partially filled in', function(){
           expect(typeof(NHMobileForm.prototype.display_partial_reasons)).toBe('function');
        });

        it('Has functionality to submit a completed form to the server', function(){
           expect(typeof(NHMobileForm.prototype.submit_observation)).toBe('function');
        });

        it('Has functionality to display cancellation reasons if cancelling a notification', function(){
           expect(typeof(NHMobileForm.prototype.cancel_notification)).toBe('function');
        });

        it('Has functionality to submit a partially filled form to the server', function(){
           expect(typeof(NHMobileForm.prototype.process_partial_submit)).toBe('function');
        });

        it('Has functionality to submit a form that has a score', function(){
           expect(typeof(NHMobileForm.prototype.process_post_score_submit)).toBe('function');
        });

        describe('Trying to submit an invalid form', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'validate').and.callThrough();
                spyOn(NHMobileForm.prototype, 'submit_observation');
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                // spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function() {
                    var promise = new Promise();
                     var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                        '<input type="submit" value="Test Submit" id="submit" class="exclude">' +
                        '<div class="block obsField" id="parent_valid_input">' +
                        '<div class="input-header">' +
                        '<label for="test_int">Valid input</label>' +
                        '<input type="number" value="1" name="valid_input" id="valid_input" step="1" min="0" max="10" data-required="false" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div class="block obsField" id="parent_invalid_input">' +
                        '<div class="input-header">' +
                        '<label for="test_int">Invalid input</label>' +
                        '<input type="number" name="invalid_input" id="invalid_input" step="1" min="10" max="100" value="1" data-required="false" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Shows the user a popup to inform them of errors in the form when submitting a form with errors', function() {
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function () {
                    event.preventDefault();
                    return false;
                });
                var submitButton = document.getElementById('submit');
                var invalidInput = document.getElementById('invalid_input');

                // change event
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('change', false, true, false);
                invalidInput.dispatchEvent(changeEvent);

                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation).not.toHaveBeenCalled();
                //expect(submitButton.getAttribute('disabled')).toBe('disabled');

                // check modal was called
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('invalid_form');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Form contains errors');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>The form contains errors, please correct the errors and resubmit</p>');

                // choose an option and click the submit button
                var dialog = document.getElementById('invalid_form');
                var canbuttons = dialog.getElementsByTagName('a');
                var canbutton = canbuttons[0]; // should be confirm button
                var canEvent = document.createEvent('CustomEvent');
                canEvent.initCustomEvent('click', false, true, false);
                canbutton.dispatchEvent(canEvent);

                invalidInput.value = 90;

                // change event
                var changeEvent2 = document.createEvent('CustomEvent');
                changeEvent2.initCustomEvent('change', false, true, false);
                invalidInput.dispatchEvent(changeEvent2);

                expect(NHMobileForm.prototype.validate).toHaveBeenCalled();

                // click event
                var clickEvent2 = document.createEvent('CustomEvent');
                clickEvent2.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent2);

                // check that process_partial_submit has been called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
            });
        });

        describe('Submitting a partial form', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'submit_observation').and.callThrough();
                spyOn(NHMobileForm.prototype, 'display_partial_reasons').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_partial_submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function() {
                    var url = NHMobileForm.prototype.process_request.calls.mostRecent().args[1];
                    var promise = new Promise();
                    if (url == 'http://localhost:8069/mobile/test/partial_reasons/') {
                        var partial_reasons = new NHMobileData({
                            status: 'success',
                            title: 'Reason for partial observation',
                            description: 'Please state reason for submitting partial observation',
                            data: [[1,'Option 1'], [2, 'Option 2']]
                        });
                        promise.complete(partial_reasons);
                    }else if(url == 'http://localhost:8069/mobile/task/submit_ajax/test/0'){
                        var obs_submit = new NHMobileData({
                            status: 'success',
                            title: 'Successfully submitted observation',
                            description: 'Here are related tasks based on the observation',
                            data: {
                                status: 1,
                                related_tasks: []
                            }
                        })
                        promise.complete(obs_submit)
                    }else{
                         var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    }
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                        '<input type="submit" value="Test Submit" id="submit" class="exclude">' +
                        '<div class="block obsField" id="parent_complete_input">' +
                        '<div class="input-header">' +
                        '<label for="complete_input">Test Complete Input</label>' +
                        '<input type="number" value="1" name="complete_input" id="complete_input" data-required="false" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div class="block obsField" id="parent_incomplete_input">' +
                        '<div class="input-header">' +
                        '<label for="incomplete_input">Test Incomplete Input</label>' +
                        '<input type="number" name="incomplete_input" id="incomplete_input" data-required="false" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Shows a list of partial observation reasons when submitting a form that is incomplete, on selecting a reason sends this to the server', function() {
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function () {
                    event.preventDefault();
                    return false;
                });
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(NHMobileForm.prototype.display_partial_reasons).toHaveBeenCalled();
                expect(NHMobileForm.prototype.process_request).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');

                // check modal was called
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('partial_reasons');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Reason for partial observation');
                // failing due to data from server not being correct
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Please state reason for submitting partial observation</p><select name="partial_reason"><option value="1">Option 1</option><option value="2">Option 2</option></select>');

                // choose an option and click the submit button
                var dialog = document.getElementById('partial_reasons');
                var select = dialog.getElementsByTagName('select')[0];
                select.value = 1;
                var canbuttons = dialog.getElementsByTagName('a');
                var conbutton = canbuttons[1]; // should be confirm button
                var conEvent = document.createEvent('CustomEvent');
                conEvent.initCustomEvent('click', false, true, false);
                NHModal.prototype.create_dialog.calls.reset();
                conbutton.dispatchEvent(conEvent);

                // check that process_partial_submit has been called
                expect(NHMobileForm.prototype.process_partial_submit).toHaveBeenCalled();
                //expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.process_request).toHaveBeenCalled();

                // check that modal was called
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_success');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Successfully submitted observation');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Here are related tasks based on the observation</p>');

            });
        });

        describe('Submitting a partial notification form', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'submit_observation').and.callThrough();
                spyOn(NHMobileForm.prototype, 'display_partial_reasons').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_partial_submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function() {
                    var url = NHMobileForm.prototype.process_request.calls.mostRecent().args[1];
                    var promise = new Promise();
                    promise.complete([{}]);
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test_notification" ajax-args="test,0">' +
                        '<input type="submit" value="Test Submit" id="submit" class="exclude">' +
                        '<div class="block obsField" id="parentcomplete_input">' +
                        '<div class="input-header">' +
                        '<label for="complete_input">Test Complete Input</label>' +
                        '<input type="number" value="1" name="complete_input" id="complete_input" data-required="false" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div class="block obsField" id="parent_incomplete_input">' +
                        '<div class="input-header">' +
                        '<label for="incomplete_input">Test incomplete_input</label>' +
                        '<input type="number" name="incomplete_input" id="incomplete_input" data-required="false" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Shows a popup to say the form contains empty elements as notifications cannot have partial submissions', function() {
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function () {
                    event.preventDefault();
                    return false;
                });
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(NHMobileForm.prototype.display_partial_reasons).not.toHaveBeenCalled();
                expect(NHMobileForm.prototype.process_request).not.toHaveBeenCalled();
                //expect(submitButton.getAttribute('disabled')).toBe('disabled');

                // check modal was called
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('invalid_form');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Form contains empty fields');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>The form contains empty fields, please enter data into these fields and resubmit</p>');
            });
        });

        describe('Submitting a clinical cancellation', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'submit_observation').and.callThrough();
                spyOn(NHMobileForm.prototype, 'cancel_notification').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_partial_submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function() {
                    var url = NHMobileForm.prototype.process_request.calls.mostRecent().args[1];
                    var promise = new Promise();
                    if (url == 'http://localhost:8069/mobile/tasks/cancel_reasons/') {
                        var cancel_reasons = new NHMobileData({
                            status: 'success',
                            title: 'Reason for cancelling task?',
                            description: 'Please state reason for cancelling task',
                            data: [
                                {
                                    id: 1,
                                    name: 'Option 1'
                                },
                                {
                                    id: 2,
                                    name: 'Option 2'
                                }
                            ]
                        })
                        promise.complete(cancel_reasons);
                    }else if(url == 'http://localhost:8069/mobile/tasks/cancel_clinical/test'){
                        var cancel_submit = new NHMobileData({
                            status: 'success',
                            title: 'Cancellation successful',
                            description: 'The notification was successfully cancelled',
                            data: {
                                status: 4,
                                related_tasks: []
                            }
                        })
                        promise.complete(cancel_submit)
                    }else{
                         var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    }
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                        '<input type="submit" value="Test Submit" id="submit" class="exclude">' +
                        '<p class="obsConfirm">' +
                        '<input type="reset" ajax-action="/mobile/tasks/cancel_clinical/1" class="button cancelButton exclude" id="cancelSubmit" value="Cancel action">' +
                        '</p>' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Shows a list of cancel reasons on pressing the cancel button, then when pressing submit sends a partial observation to the server', function() {
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function () {
                    event.preventDefault();
                    return false;
                });
                var cancel_button = document.getElementById('cancelSubmit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                cancel_button.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.cancel_notification).toHaveBeenCalled();
                expect(NHMobileForm.prototype.process_request).toHaveBeenCalled();
                //expect(cancel_button.getAttribute('disabled')).toBe('disabled');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('cancel_reasons');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Reason for cancelling task?');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Please state reason for cancelling task</p><select name="reason"><option value="1">Option 1</option><option value="2">Option 2</option></select>');

                // choose an option and click the submit button
                var dialog = document.getElementById('cancel_reasons');
                var select = dialog.getElementsByTagName('select')[0];
                select.value = 1;
                var canbuttons = dialog.getElementsByTagName('a');
                var conbutton = canbuttons[1]; // should be confirm button
                var conEvent = document.createEvent('CustomEvent');
                conEvent.initCustomEvent('click', false, true, false);
                NHModal.prototype.create_dialog.calls.reset();
                conbutton.dispatchEvent(conEvent);

                // check that process_partial_submit has been called
                expect(NHMobileForm.prototype.process_partial_submit).toHaveBeenCalled();
                //expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.process_request).toHaveBeenCalled();

                // check that modal was called
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('cancel_success');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Cancellation successful');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>The notification was successfully cancelled</p>');

            });
        });

        describe('Submitting a form that requires a pre submit action', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'submit_observation').and.callThrough();
                spyOn(NHMobileForm.prototype, 'cancel_notification').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_post_score_submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'display_partial_reasons').and.callThrough();
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
                spyOn(NHModal.prototype, 'close_modal').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var url= NHMobileForm.prototype.process_request.calls.mostRecent().args[1];
                    var promise = new Promise();
                    if(url == 'http://localhost:8069/mobile/test/test/0') {
                        var calculate_score = new NHMobileData({
                            status: 'success',
                            title: 'Submit TEST score of 0',
                            description: 'TEST observation scored 0 which means something',
                            data: {
                                status: 3,
                                next_action: 'json_task_form_action',
                                score: {
                                    score: 0
                                }
                            }
                        });
                        promise.complete(calculate_score);
                    }else if(url == 'http://localhost:8069/mobile/test/test/partial') {
                        var calculate_score = new NHMobileData({
                            status: 'success',
                            title: 'Submit TEST score of 0',
                            description: 'TEST observation scored 0 which means something',
                            data: {
                                status: 3,
                                next_action: 'json_task_form_action',
                                score: {
                                    score: 0
                                }
                            }
                        });
                        promise.complete(calculate_score);
                    }else if (url == 'http://localhost:8069/mobile/test/partial_reasons/') {
                        var partial_reasons = new NHMobileData({
                            status: 'success',
                            title: 'Reason for partial observation',
                            description: 'Please state reason for submitting partial observation',
                            data: [[1,'Option 1'], [2, 'Option 2']]
                        });
                        promise.complete(partial_reasons);
                    }else if(url == 'http://localhost:8069/mobile/task/submit_ajax/test/0'){
                        var obs_submit = new NHMobileData({
                            status: 'success',
                            title: 'Successfully submitted observation',
                            description: 'Here are related tasks based on the observation',
                            data: {
                                status: 1,
                                related_tasks: []
                            }
                        })
                        promise.complete(obs_submit);
                    }else if(url == 'http://localhost:8069/mobile/test/test/1'){
                        var calculate_score = new NHMobileData({
                            status: 'success',
                            title: 'Submit TEST score of 0',
                            description: 'TEST observation scored 0 which means something',
                            data: {
                                status: 3,
                                next_action: 'json_task_form_action',
                                score: {
                                    score: 0,
                                    clinical_risk: 'low'
                                }
                            }
                        });
                        promise.complete(calculate_score);
                    }else{
                         var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                        promise.complete(empty);
                    }
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0" ajax-partial-action="score">' +
                        '<input type="submit" value="Test Submit" id="submit" class="exclude">' +
                        '<div class="block obsField" id="parent_test_int">' +
                        '<div class="input-header">' +
                        '<label for="test_int">Test Integer</label>' +
                        '<input type="number" value="1" name="test_int" id="test_int" min="0" max="10" step="1" data-required="false" data-necessary="true">' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Executes a pre submit function, presents popup and on submit in popup being pressed sends data to server - No triggered tasks', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.count()).toBe(1);
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,0');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_observation')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Submit TEST score of 0 for Test Patient?')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('TEST observation scored 0 which means something');
                var option_buttons = NHModal.prototype.create_dialog.calls.mostRecent().args[4]
                expect(option_buttons[1]).toBe('<a href="#" data-target="submit_observation" data-action="submit" data-ajax-action="json_task_form_action">Submit</a>');

                // click the submit button
                var dialog = document.getElementById('submit_observation');
                var options = dialog.getElementsByTagName('a');
                var option = options[1];
                var submitEvent = document.createEvent('CustomEvent');
                submitEvent.initCustomEvent('click', false, true, false);
                NHMobileForm.prototype.submit_observation.calls.reset();
                option.dispatchEvent(submitEvent);

                // verify submit called again
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(document.getElementById('submit_observation')).toBe(null);
                expect(NHModal.prototype.handle_button_events).toHaveBeenCalled();
                expect(NHModal.prototype.close_modal).toHaveBeenCalled();
                expect(NHMobileForm.prototype.process_post_score_submit).toHaveBeenCalled();
                /* Currently not working due to some weird scope bug */
                //expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                //expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('json_task_form_action');
                //expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,0');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_success')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Successfully submitted observation')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Here are related tasks based on the observation</p>');

            });

            it('Executes a pre submit function, presents popup with clinical risk', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                form.setAttribute('ajax-args', 'test,1');
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.count()).toBe(1);
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,1');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_observation')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Submit TEST score of 0 for Test Patient?')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('TEST observation scored 0 which means something');
                var option_buttons = NHModal.prototype.create_dialog.calls.mostRecent().args[4]
                expect(option_buttons[1]).toBe('<a href="#" data-target="submit_observation" data-action="submit" data-ajax-action="json_task_form_action">Submit</a>');

                // click the submit button
                var dialog = document.getElementById('submit_observation');
                expect(dialog.classList.contains('clinicalrisk-low')).toBe(true);
            });

            it('Executes a pre submit function, presents popup and on close popup it renables form', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.count()).toBe(1);
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,0');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_observation')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Submit TEST score of 0 for Test Patient?')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('TEST observation scored 0 which means something');
                var option_buttons = NHModal.prototype.create_dialog.calls.mostRecent().args[4]
                expect(option_buttons[1]).toBe('<a href="#" data-target="submit_observation" data-action="submit" data-ajax-action="json_task_form_action">Submit</a>');

                // click the submit button
                var dialog = document.getElementById('submit_observation');
                var options = dialog.getElementsByTagName('a');
                var option = options[0];
                var submitEvent = document.createEvent('CustomEvent');
                submitEvent.initCustomEvent('click', false, true, false);
                option.dispatchEvent(submitEvent);

                // verify submit called again
                expect(submitButton.getAttribute('disabled')).toBe(null);
                expect(document.getElementById('submit_observation')).toBe(null);
            });

            it('Executes a pre partial reasons function if partial and defined on form', function(){
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                form.setAttribute('ajax-args', 'test,partial');
                var input = document.getElementById('test_int');
                input.value = null;

                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.count()).toBe(1);
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,partial');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_observation');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Submit TEST score of 0 for Test Patient?')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('TEST observation scored 0 which means something');
                var option_buttons = NHModal.prototype.create_dialog.calls.mostRecent().args[4]
                expect(option_buttons[1]).toBe('<a href="#" data-target="submit_observation" data-action="display_partial_reasons" data-ajax-action="json_task_form_action">Submit</a>');

                // click the submit button
                var dialog = document.getElementById('submit_observation');
                var options = dialog.getElementsByTagName('a');
                var option = options[1];
                var submitEvent = document.createEvent('CustomEvent');
                submitEvent.initCustomEvent('click', false, true, false);
                option.dispatchEvent(submitEvent);

                // Ensure that partial reason dialog pops up after
                expect(document.getElementById('submit_observation')).toBe(null);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('partial_reasons');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Reason for partial observation');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Please state reason for submitting partial observation</p><select name="partial_reason"><option value="1">Option 1</option><option value="2">Option 2</option></select>');

                // Choose a reason and press submit
                var dialog = document.getElementById('partial_reasons');
                var select = dialog.getElementsByTagName('select')[0];
                select.value = 1;
                var options = dialog.getElementsByTagName('a');
                var option = options[1];
                var submitEvent = document.createEvent('CustomEvent');
                submitEvent.initCustomEvent('click', false, true, false);
                option.dispatchEvent(submitEvent);

                expect(document.getElementById('partial_reasons')).toBe(null);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_success')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Successfully submitted observation')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Here are related tasks based on the observation</p>');
            });
        });

        describe('Submitting a normal form', function(){
            var mobile;
            afterEach(function(){
                cleanUp();

            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'submit_observation').and.callThrough();
                spyOn(NHMobileForm.prototype, 'cancel_notification').and.callThrough();
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var url= NHMobileForm.prototype.process_request.calls.mostRecent().args[1];
                    var promise = new Promise();
                    if(url == 'http://localhost:8069/mobile/test/test/0'){
                        var obs_submit = new NHMobileData({
                            status: 'success',
                            title: 'Successfully submitted observation',
                            description: 'Here are related tasks based on the observation',
                            data: {
                                status: 1,
                                related_tasks: []
                            }
                        })
                        promise.complete(obs_submit);
                    }else if(url == 'http://localhost:8069/mobile/test/test/1'){
                        var obs_submit = new NHMobileData({
                            status: 'success',
                            title: 'Action required',
                            description: 'Here are related tasks based on the observation',
                            data: {
                                status: 1,
                                related_tasks: [
                                    {
                                        summary: 'Test Task',
                                        id: 1337
                                    }
                                ]
                            }
                        })
                        promise.complete(obs_submit);
                    }else if(url == 'http://localhost:8069/mobile/test/test/2'){
                        var obs_submit = new NHMobileData({
                            status: 'success',
                            title: 'Action required',
                            description: 'Here are related tasks based on the observation',
                            data: {
                                status: 1,
                                related_tasks: [
                                    {
                                        summary: 'Test Task',
                                        id: 1337
                                    },
                                    {
                                        summary: 'Test Task 2',
                                        id: 666
                                    }
                                ]
                            }
                        })
                        promise.complete(obs_submit);
                    }else{
                          var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    }
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                        '<input type="submit" value="Test Submit" id="submit" class="exclude">' +
                        '<div class="block obsField" id="parent_test_int">' +
                        '<div class="input-header">' +
                        '<label for="test_int">Test Integer</label>' +
                        '<input type="number" value="1" name="test_int" id="test_int" min="0" max="10" step="1" data-required="false" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Sends data to the server on a valid form being submitted via submit button - No triggered tasks', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,0');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_success')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Successfully submitted observation')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Here are related tasks based on the observation</p>');
            });

            it('Sends data to the server on a valid form being submitted via submit button - 1 Triggered task', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                form.setAttribute('ajax-args', 'test,1');
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,1');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_success')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Action required')
                //expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<ul class="menu"><li><a href="http://localhost:8069/mobile/task/1337">Test Task</a></li></ul>');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Test Task</p>');
            });

            it('Sends data to the server on a valid form being submitted via submit button - 2 Triggered tasks', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                form.setAttribute('ajax-args', 'test,2');
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,2');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_success')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Action required')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<ul class="menu"><li><a href="http://localhost:8069/mobile/task/1337">Test Task</a></li><li><a href="http://localhost:8069/mobile/task/666">Test Task 2</a></li></ul>');
            });

            it('Sends data to the server on a valid form being submitted via submit button - Server Error', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                form.setAttribute('ajax-args', 'test,3');
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe(null);
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,3');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_error')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Error submitting observation')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('Server returned an error');
            });
        });

        describe('Submitting a form with empty required fields', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'submit_observation').and.callThrough();
                spyOn(NHMobileForm.prototype, 'display_partial_reasons').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_partial_submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callThrough();
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                        '<input type="submit" value="Test Submit" id="submit" class="exclude">' +
                        '<div class="block obsField" id="parent_complete_input">' +
                        '<div class="input-header">' +
                        '<label for="complete_input">Test Complete Input</label>' +
                        '<input type="number" value="1" name="complete_input" id="complete_input" data-required="false" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div class="block obsField" id="parent_incomplete_mandatory_input">' +
                        '<div class="input-header">' +
                        '<label for="incomplete_mandatory_input">Test Incomplete Mandatory Input</label>' +
                        '<input type="number" name="incomplete_mandatory_input" id="incomplete_mandatory_input" data-required="true" data-necessary="true">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Shows message explaining mandatory fields need to be completed before submission', function() {
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function () {
                    event.preventDefault();
                    return false;
                });
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();

                // check modal was called
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('invalid_form');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Form contains empty fields');
                // failing due to data from server not being correct
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>The form contains empty fields, please enter data into these fields and resubmit</p>');
            });
        });

        describe('Submitting a partial form with empty optional fields', function(){
            var mobile;
            afterEach(function(){
                cleanUp();
                mobile = null;
            });

            beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'submit_observation').and.callThrough();
                spyOn(NHMobileForm.prototype, 'display_partial_reasons').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_partial_submit').and.callThrough();
                spyOn(NHMobileForm.prototype, 'get_patient_info');
                spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                spyOn(NHModal.prototype, 'handle_button_events').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function() {
                    var url = NHMobileForm.prototype.process_request.calls.mostRecent().args[1];
                    var promise = new Promise();
                    if(url == 'http://localhost:8069/mobile/test/test/0'){
                        var obs_submit = new NHMobileData({
                            status: 'success',
                            title: 'Successfully submitted observation',
                            description: 'Here are related tasks based on the observation',
                            data: {
                                status: 1,
                                related_tasks: []
                            }
                        })
                        promise.complete(obs_submit)
                    }else{
                         var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    }
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                        '<input type="submit" value="Test Submit" id="submit" class="exclude">' +
                        '<div class="block obsField" id="parent_complete_input">' +
                        '<div class="input-header">' +
                        '<label for="complete_input">Test Complete Input</label>' +
                        '<input type="number" value="1" name="complete_input" id="complete_input" data-necessary="true" data-required="false">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div class="block obsField" id="parent_incomplete_input">' +
                        '<div class="input-header">' +
                        '<label for="incomplete_input">Test Incomplete Optional Input</label>' +
                        '<input type="number" name="incomplete_input" id="incomplete_input" data-necessary="false" data-required="false">' +
                        '</div>' +
                        '<div class="input-body">' +
                        '<span class="errors"></span>' +
                        '<span class="help"></span>' +
                        '</div>' +
                        '</div>' +
                        '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                        '</form>'
                mobile = new NHMobileForm();
            });

            it('Considers the form complete as all non-optional fields have values', function() {
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function () {
                    event.preventDefault();
                    return false;
                });
                var submitButton = document.getElementById('submit');

                // click event
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                submitButton.dispatchEvent(clickEvent);

                //verify submit called
                expect(NHMobileForm.prototype.submit).toHaveBeenCalled();
                expect(submitButton.getAttribute('disabled')).toBe('disabled');
                expect(NHMobileForm.prototype.submit_observation).toHaveBeenCalled();
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[2]).toBe('test');
                expect(NHMobileForm.prototype.submit_observation.calls.mostRecent().args[3]).toBe('test,0');
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('submit_success')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Successfully submitted observation')
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<p>Here are related tasks based on the observation</p>');

            });
        });

    });

    describe('Form Interaction', function(){
        afterEach(function(){
           cleanUp();
        });

        it('Has functionality to trigger actions based on interactions with a form', function(){
           expect(typeof(NHMobileForm.prototype.trigger_actions)).toBe('function');
        });

        it('Has functionality to show a reference image or iframe for a form input', function(){
           expect(typeof(NHMobileForm.prototype.show_reference)).toBe('function');
        });

        it('Has functionality to hide inputs if a triggered action says we need to', function(){
           expect(typeof(NHMobileForm.prototype.hide_triggered_elements)).toBe('function');
        });

        it('Has functionality to show inputs if a triggered action says we need to', function(){
           expect(typeof(NHMobileForm.prototype.show_triggered_elements)).toBe('function');
        });

        it('Has functionality to disable inputs if a triggered action says we need to', function(){
           expect(typeof(NHMobileForm.prototype.disable_triggered_elements)).toBe('function');
        });

        it('Has functionality to enable inputs if a triggered action says we need to', function(){
           expect(typeof(NHMobileForm.prototype.enable_triggered_elements)).toBe('function');
        });

        describe('Showing and Hiding elements based on triggered actions', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'reset_input_errors');
                spyOn(NHMobileForm.prototype, 'trigger_actions').and.callThrough();
                spyOn(NHMobileForm.prototype, 'hide_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'show_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                     var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    return promise;
                });

                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<select name="origin_element" id="origin_element" data-onchange="[' +
                    '{\'action\': \'show\', \'fields\': [\'hidden_affected_element\'], \'condition\': [[\'origin_element\', \'==\', 2]], \'type\': \'value\'}, ' +
                    '{\'action\': \'hide\', \'fields\': [\'affected_element\'], \'condition\': [[\'origin_element\', \'==\', 1]], \'type\': \'value\'}, ' +
                    '{\'action\': \'hide\', \'fields\': [\'affected_element\', \'hidden_affected_element\'], \'condition\': [[\'origin_element\', \'==\', \'\']], \'type\': \'value\'}]" '+
                    'data-required="false" data-necessary="true">' +
                    '<option value="">Default</option>' +
                    '<option value="1">Hide</option>' +
                    '<option value="2">Show</option>' +
                    '</select>' +
                    '<div id="parent_affected_element">' +
                    '<input type="number" id="affected_element" data-required="false" data-necessary="true">' +
                    '</div>' +
                    '<div id="parent_hidden_affected_element" style="display: none;">' +
                    '<input type="number" id="hidden_affected_element" class="exclude" data-required="false" data-necessary="false">' +
                    '</div>' +
                    '<div id="parent_field_changer">' +
                    '<input type="number" id="field_changer" data-required="false" data-necessary="true" data-onchange="[' +
                    '{\'action\': \'show\', \'fields\': [\'hidden_affected_element\'], \'condition\': [[\'field_changer\', \'==\', \'field_to_compare\']], \'type\': \'field\'},' +
                    '{\'action\': \'hide\', \'fields\': [\'hidden_affected_element\'], \'condition\': [[\'field_changer\', \'!=\', \'field_to_compare\']], \'type\': \'field\'}]">' +
                    '</div>' +
                    '<div id="parent_field_to_compare" style="display: none;">' +
                    '<input type="number" id="field_to_compare" class="exclude" data-required="false" data-necessary="false" value="666">' +
                    '</div>' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
                var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
            });

            afterEach(function(){
               cleanUp();
                mobile = null;
            });

            describe('Value Based Triggered Actions', function(){
                it('Hides the input mentioned in the data-onchange attribute when the hide condition is met', function(){
                    var origin_element = document.getElementById('origin_element');
                    var parent_element = document.getElementById('parent_affected_element');
                    var element = document.getElementById('affected_element');
                    expect(parent_element.style.display).not.toBe('none');
                    expect(element.classList.contains('exclude')).not.toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('true');
                    origin_element.value = 1;
                    var changeEvent = document.createEvent('CustomEvent');
                    changeEvent.initCustomEvent('change', false, true, false);
                    origin_element.dispatchEvent(changeEvent);
                    expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.hide_triggered_elements).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.hide_triggered_elements.calls.mostRecent().args[0]).toBe('affected_element');
                    expect(parent_element.style.display).toBe('none');
                    expect(element.classList.contains('exclude')).toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('false');
                });

                it('Hides input mentioned in the data-onchange attribute when the hide condition is met (no value set)', function(){
                    var origin_element = document.getElementById('origin_element');
                    var parent_element = document.getElementById('parent_affected_element');
                    var element = document.getElementById('affected_element');
                    var parent_hidden_element = document.getElementById('parent_hidden_affected_element');
                    var hidden_element = document.getElementById('hidden_affected_element');
                    expect(parent_element.style.display).not.toBe('none');
                    expect(parent_hidden_element.style.display).toBe('none');
                    expect(element.classList.contains('exclude')).not.toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('true');
                    expect(hidden_element.classList.contains('exclude')).toBe(true);
                    origin_element.value = '';
                    var changeEvent = document.createEvent('CustomEvent');
                    changeEvent.initCustomEvent('change', false, true, false);
                    origin_element.dispatchEvent(changeEvent);
                    expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.hide_triggered_elements).toHaveBeenCalled();
                    expect(parent_element.style.display).toBe('none');
                    expect(parent_hidden_element.style.display).toBe('none');
                    expect(element.classList.contains('exclude')).toBe(true);
                    expect(hidden_element.classList.contains('exclude')).toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('false');
                });

                it('Shows the input mentioned in the data-onchange attribute when the show condition is met', function(){
                    var origin_element = document.getElementById('origin_element');
                    var parent_element = document.getElementById('parent_hidden_affected_element');
                    var element = document.getElementById('hidden_affected_element');
                    expect(parent_element.style.display).toBe('none');
                    expect(element.classList.contains('exclude')).toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('false');
                    origin_element.value = 2;
                    var changeEvent = document.createEvent('CustomEvent');
                    changeEvent.initCustomEvent('change', false, true, false);
                    origin_element.dispatchEvent(changeEvent);
                    expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.show_triggered_elements).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.show_triggered_elements.calls.mostRecent().args[0]).toBe('hidden_affected_element');
                    expect(parent_element.style.display).not.toBe('none');
                    expect(element.classList.contains('exclude')).not.toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('true');
                });
            });

            describe('Field Comparison Based Triggered Actions', function(){
                it('Shows the input mentioned in the data-onchange attribute when the show condition is met', function(){
                    var origin_element = document.getElementById('field_changer');
                    var parent_element = document.getElementById('parent_hidden_affected_element');
                    var element = document.getElementById('hidden_affected_element');
                    expect(parent_element.style.display).toBe('none');
                    expect(element.classList.contains('exclude')).toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('false');
                    origin_element.value = 666;
                    var changeEvent = document.createEvent('CustomEvent');
                    changeEvent.initCustomEvent('change', false, true, false);
                    origin_element.dispatchEvent(changeEvent);
                    expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.show_triggered_elements).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.show_triggered_elements.calls.mostRecent().args[0]).toBe('hidden_affected_element');
                    expect(parent_element.style.display).not.toBe('none');
                    expect(element.classList.contains('exclude')).not.toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('true');
                });
                it('Hides the input mentioned in the data-onchange attribute when the hide condition is met', function(){
                    var origin_element = document.getElementById('field_changer');
                    var parent_element = document.getElementById('parent_hidden_affected_element');
                    var element = document.getElementById('hidden_affected_element');
                    parent_element.style.display = 'block';
                    element.classList.remove('exclude');
                    element.setAttribute('data-necessary', 'true');
                    expect(parent_element.style.display).toBe('block');
                    expect(element.classList.contains('exclude')).toBe(false);
                    expect(element.getAttribute('data-necessary')).toBe('true');
                    origin_element.value = 2;
                    var changeEvent = document.createEvent('CustomEvent');
                    changeEvent.initCustomEvent('change', false, true, false);
                    origin_element.dispatchEvent(changeEvent);
                    expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.hide_triggered_elements).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.hide_triggered_elements.calls.mostRecent().args[0]).toBe('hidden_affected_element');
                    expect(parent_element.style.display).toBe('none');
                    expect(element.classList.contains('exclude')).toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('false');
                });
                it('Hides the input mentioned in the data-onchange attribute when the hide condition is met - no value set', function(){
                    var origin_element = document.getElementById('field_changer');
                    var parent_element = document.getElementById('parent_hidden_affected_element');
                    var element = document.getElementById('hidden_affected_element');
                    parent_element.style.display = 'block';
                    element.classList.remove('exclude');
                    element.setAttribute('data-necessary', 'true');
                    expect(parent_element.style.display).toBe('block');
                    expect(element.classList.contains('exclude')).toBe(false);
                    expect(element.getAttribute('data-necessary')).toBe('true');
                    origin_element.value = null;
                    var changeEvent = document.createEvent('CustomEvent');
                    changeEvent.initCustomEvent('change', false, true, false);
                    origin_element.dispatchEvent(changeEvent);
                    expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.hide_triggered_elements).toHaveBeenCalled();
                    expect(NHMobileForm.prototype.hide_triggered_elements.calls.mostRecent().args[0]).toBe('hidden_affected_element');
                    expect(parent_element.style.display).toBe('none');
                    expect(element.classList.contains('exclude')).toBe(true);
                    expect(element.getAttribute('data-necessary')).toBe('false');
                });
            });
        });

        describe('Enabling and Disabling elements based on triggered actions', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'trigger_actions').and.callThrough();
                spyOn(NHMobileForm.prototype, 'disable_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'enable_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'validate');
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                    var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<select name="origin_element" id="origin_element" data-onchange="[{\'action\': \'enable\', \'fields\': [\'disabled_affected_element\'], \'condition\': [[\'origin_element\', \'==\', \'True\']]}, {\'action\': \'disable\', \'fields\': [\'affected_element\'], \'condition\': [[\'origin_element\', \'==\', \'False\']]}]" data-required="false" data-necessary="true">' +
                    '<option value="">Default</option>' +
                    '<option value="False">Disable</option>' +
                    '<option value="True">Enable</option>' +
                    '</select>' +
                    '<input type="number" id="affected_element" data-required="false" data-necessary="true">' +
                    '<input type="number" id="disabled_affected_element" class="exclude" disabled="disabled" data-required="false" data-necessary="false">' +
                    '<input type="number" id="value_change" data-onchange="[{\'action\': \'disable\', \'fields\': [\'origin_element\'], \'condition\': [[\'value_change\', \'!=\', \'affected_element\']]}]" data-required="false" data-necessary="true">'+
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
                mobile = null;
            });

            it('Disables the input mentioned in the data-onchange attribute when the disable condition is met', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('affected_element');
                expect(element.classList.contains('exclude')).not.toBe(true);
                expect(element.disabled).not.toBe(true);
                expect(element.getAttribute('data-necessary')).toBe('true');
                origin_element.value = "False";
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(changeEvent);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.disable_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.disable_triggered_elements.calls.mostRecent().args[0]).toBe('affected_element');
                expect(element.classList.contains('exclude')).toBe(true);
                expect(element.disabled).toBe(true);
                expect(element.getAttribute('data-necessary')).toBe('false');
            });

            it('Disables the input mentioned in the data-onchange attribute when the disable condition is met (comparative value)', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('affected_element');
                var value_change = document.getElementById('value_change');
                element.value = 666;
                value_change.value = 1337;
                expect(origin_element.classList.contains('exclude')).not.toBe(true);
                expect(origin_element.disabled).not.toBe(true);
                expect(origin_element.getAttribute('data-necessary')).toBe('true');
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('change', false, true, false);
                value_change.dispatchEvent(changeEvent);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.disable_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.disable_triggered_elements.calls.mostRecent().args[0]).toBe('origin_element');
                expect(origin_element.classList.contains('exclude')).toBe(true);
                expect(origin_element.disabled).toBe(true);
                expect(origin_element.getAttribute('data-necessary')).toBe('false');
            });

            it('Enables the input mentioned in the data-onchange attribute when the enable condition is met', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('disabled_affected_element');
                expect(element.classList.contains('exclude')).toBe(true);
                expect(element.disabled).toBe(true);
                expect(element.getAttribute('data-necessary')).toBe('false');
                origin_element.value = "True";
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(changeEvent);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.enable_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.enable_triggered_elements.calls.mostRecent().args[0]).toBe('disabled_affected_element');
                expect(element.classList.contains('exclude')).not.toBe(true);
                expect(element.disabled).not.toBe(true);
                expect(element.getAttribute('data-necessary')).toBe('true');
            });
        });

        describe('Making elements mandatory or not mandatory based on triggered actions', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'trigger_actions').and.callThrough();
                spyOn(NHMobileForm.prototype, 'require_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'unrequire_triggered_elements').and.callThrough();
                spyOn(NHMobileForm.prototype, 'validate');
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                    var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    return promise;
                });
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<select name="origin_element" id="origin_element" data-onchange="[{\'action\': \'require\', \'fields\': [\'unrequired_affected_element\'], \'condition\': [[\'origin_element\', \'==\', \'True\']]}, {\'action\': \'unrequire\', \'fields\': [\'affected_element\', \'unrequired_affected_element\'], \'condition\': [[\'origin_element\', \'==\', \'False\']]}]" data-required="true" data-necessary="true">' +
                    '<option value="">Default</option>' +
                    '<option value="False">Unrequire</option>' +
                    '<option value="True">Require</option>' +
                    '</select>' +
                    '<input type="number" id="affected_element" data-required="true" data-necessary="true">' +
                    '<input type="number" id="unrequired_affected_element" class="exclude" data-required="false" data-necessary="false">' +
                    '<input type="number" id="value_change" data-onchange="[{\'action\': \'unrequire\', \'fields\': [\'origin_element\'], \'condition\': [[\'value_change\', \'!=\', \'affected_element\']], \'type\': \'field\'}]" data-required="false" data-necessary="true">'+
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
                mobile = null;
            });

            it('The input mentioned in the data-onchange attribute is no longer mandatory when the unrequire condition is met', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('affected_element');
                expect(element.classList.contains('exclude')).not.toBe(true);
                expect(element.getAttribute('data-necessary')).toBe('true');
                expect(element.getAttribute('data-required')).toBe('true');
                origin_element.value = "False";
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(changeEvent);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.unrequire_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.unrequire_triggered_elements.calls.mostRecent().args[0]).toBe('unrequired_affected_element');
                expect(element.classList.contains('exclude')).toBe(true);
                expect(element.getAttribute('data-necessary')).toBe('true');
                expect(element.getAttribute('data-required')).toBe('false');
            });

            it('The input mentioned in the data-onchange attribute is not longer mandatory when the unrequire condition is met (comparative value)', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('affected_element');
                var value_change = document.getElementById('value_change');
                element.value = 666;
                value_change.value = 1337;
                expect(origin_element.classList.contains('exclude')).not.toBe(true);
                expect(origin_element.getAttribute('data-necessary')).toBe('true');
                expect(origin_element.getAttribute('data-required')).toBe('true');
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('change', false, true, false);
                value_change.dispatchEvent(changeEvent);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.unrequire_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.unrequire_triggered_elements.calls.mostRecent().args[0]).toBe('origin_element');
                expect(origin_element.classList.contains('exclude')).toBe(true);
                expect(origin_element.getAttribute('data-necessary')).toBe('true');
                expect(origin_element.getAttribute('data-required')).toBe('false');
            });

            it('The input mentioned in the data-onchange attribute is required when the require condition is met', function(){
                var origin_element = document.getElementById('origin_element');
                var element = document.getElementById('unrequired_affected_element');
                expect(element.classList.contains('exclude')).toBe(true);
                expect(element.getAttribute('data-necessary')).toBe('false');
                expect(element.getAttribute('data-required')).toBe('false');
                origin_element.value = "True";
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('change', false, true, false);
                origin_element.dispatchEvent(changeEvent);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(NHMobileForm.prototype.require_triggered_elements).toHaveBeenCalled();
                expect(NHMobileForm.prototype.require_triggered_elements.calls.mostRecent().args[0]).toBe('unrequired_affected_element');
                expect(element.classList.contains('exclude')).not.toBe(true);
                expect(element.getAttribute('data-necessary')).toBe('false');
                expect(element.getAttribute('data-required')).toBe('true');
            });
        });

        describe('Reference buttons', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'show_reference').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                     var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    return promise;
                });
                spyOn(NHModal.prototype, 'create_dialog').and.callThrough();
                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<button id="image_reference" data-type="image" data-url="/" data-title="Test Reference Image">Test Button</button>' +
                    '<button id="iframe_reference" data-type="iframe" data-url="/" data-title="Test Reference Iframe">Test Button</button>' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
                mobile = null;
            });

            it('Shows a reference image in a modal on pressing the button', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testButton = document.getElementById('image_reference');
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                testButton.dispatchEvent(clickEvent);
                expect(NHMobileForm.prototype.show_reference).toHaveBeenCalled();
                expect(NHMobileForm.prototype.show_reference.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('popup_image');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Test Reference Image');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<img src="/"/>');
            });

            it('Shows a reference iframe in a modal on pressing the button', function(){
               var form = document.getElementById('obsForm');
                form.addEventListener('submit', function(){
                    event.preventDefault();
                    return false;
                });
                var testButton = document.getElementById('iframe_reference');
                var clickEvent = document.createEvent('CustomEvent');
                clickEvent.initCustomEvent('click', false, true, false);
                testButton.dispatchEvent(clickEvent);
                expect(NHMobileForm.prototype.show_reference).toHaveBeenCalled();
                expect(NHMobileForm.prototype.show_reference.calls.count()).toBe(1);
                expect(NHModal.prototype.create_dialog).toHaveBeenCalled();
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[1]).toBe('popup_iframe');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[2]).toBe('Test Reference Iframe');
                expect(NHModal.prototype.create_dialog.calls.mostRecent().args[3]).toBe('<iframe src="/"></iframe>');
            });
        })

        describe('Setting exclude classes on unselected radio inputs', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'trigger_actions').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                     var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    return promise;
                });

                var test = document.getElementById('test');
                test.innerHTML = '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<input type="radio" name="radio_1" id="radio_1" value="1">' +
                    '<input type="radio" name="radio_1" id="radio_2" value="2">' +
                    '<input type="radio" name="radio_1" id="radio_3" value="3">' +
                    '<input type="radio" name="radio_jackie" id="radio_jackie" value="3">' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
                mobile = null;
            });

            it('Adds a class of exclude to all radio inputs with the same name that do not have the same value', function(){
                var radio_1 = document.getElementById('radio_1');
                var radio_2 = document.getElementById('radio_2');
                var radio_3 = document.getElementById('radio_3');
                var radio_jackie = document.getElementById('radio_jackie');
                radio_1.checked = true;
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('click', false, true, false);
                radio_1.dispatchEvent(changeEvent);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(radio_1.classList.contains('exclude')).not.toBe(true);
                expect(radio_2.classList.contains('exclude')).toBe(true);
                expect(radio_3.classList.contains('exclude')).toBe(true);
                expect(radio_jackie.classList.contains('exclude')).not.toBe(true);
            });
        });

        describe('Setting exclude classes on unselected checkbox inputs', function(){
            var mobile;
             beforeEach(function(){
                spyOn(NHMobileForm.prototype, 'submit');
                spyOn(NHMobileForm.prototype, 'handle_timeout');
                spyOn(NHMobileForm.prototype, 'trigger_actions').and.callThrough();
                spyOn(NHMobileForm.prototype, 'process_request').and.callFake(function(){
                    var promise = new Promise();
                     var empty = new NHMobileData({
                               status: 'success',
                               title: '',
                               description: '',
                               data: {}
                           })
                     promise.complete(empty);
                    return promise;
                });

                var test = document.getElementById('test');
                test.innerHTML =
                    '<form action="test" method="POST" data-type="test" task-id="0" patient-id="3" id="obsForm" data-source="task" ajax-action="test" ajax-args="test,0">' +
                    '<div id="patientName"><a patient-id="3">Test Patient</a></div>' +
                    '<div class="block obsSelectField">' +
                    '<div class="input-header">' +
                    '<label for="standard_multiselect">Standard Multiselect</label>' +
                    '</div>' +
                    '<div class="input-body">' +
                    '<ul class="checklist">' +
                    '<li>' +
                    '<input type="checkbox" name="multiselect" value="1" id="checkbox_1" class="checklist_box">' +
                    '<label>Option 1</label>' +
                    '</li>' +
                    '<li>' +
                    '<input type="checkbox" name="multiselect" value="2" id="checkbox_2" class="checklist_box">' +
                    '<label>Option 2</label>' +
                    '</li>' +
                    '</ul>' +
                    '<span class="errors"></span>' +
                    '<span class="help"></span>' +
                    '</div>' +
                    '</div>' +
                    '</form>';
                mobile = new NHMobileForm();
            });

            afterEach(function(){
               cleanUp();
                mobile = null;
            });

            it('Adds a class of exclude to all radio inputs with the same name that do not have the same value', function(){
                var checkbox1 = document.getElementById('checkbox_1');
                var checkbox2 = document.getElementById('checkbox_2');
                checkbox1.checked = true;
                var changeEvent = document.createEvent('CustomEvent');
                changeEvent.initCustomEvent('click', false, true, false);
                checkbox1.dispatchEvent(changeEvent);
                expect(NHMobileForm.prototype.trigger_actions).toHaveBeenCalled();
                expect(checkbox1.classList.contains('exclude')).not.toBe(true);
                expect(checkbox2.classList.contains('exclude')).toBe(true);
            });
        });
    });
});