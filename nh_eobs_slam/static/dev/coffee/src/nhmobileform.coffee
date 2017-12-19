# NHMobileForm contains utilities for working with the nh_eobs_mobile
# observation form
### istanbul ignore next ###
class NHMobileFormSLaM extends NHMobileForm

  cancel_notification: (self) =>
    opts = @.urls.ajax_task_cancellation_options()
    Promise.when(@call_resource(opts)).then (raw_data) ->
      server_data = raw_data[0]
      data = server_data.data
      options = ''
      for option in data
        option_val = option.id
        option_name = option.name
        options += '<option value="'+option_val+'">'+option_name+'</option>'
      select = '<select name="reason">'+options+'</select>'
      msg = '<p>' + server_data.desc + '</p>'
      can_btn = '<a href="#" data-action="close" '+
        'data-target="cancel_reasons">Cancel</a>'
      con_btn = '<a href="#" data-target="cancel_reasons" '+
        'data-action="partial_submit" '+
        'data-ajax-action="cancel_clinical_notification">Submit</a>'
      new window.NH.NHModal('cancel_reasons', server_data.title, msg+select,
        [can_btn, con_btn], 0, document.getElementsByTagName('form')[0])

  submit_observation: (self, elements, endpoint, args, partial = false) =>
    # turn form data in to serialised string and ping off to server
    formValues = {}
    for el in elements
      type = el.getAttribute('type')
      if not formValues.hasOwnProperty(el.name)
        if type is 'checkbox'
          formValues[el.name] = [el.value]
        else
          formValues[el.name] = el.value
      else
        if type is 'checkbox'
          formValues[el.name].push(el.value)
    serialised_string = (key+'='+encodeURIComponent(value) \
      for key, value of formValues).join("&")
    url = @.urls[endpoint].apply(this, args.split(','))
    # Disable the action buttons
    Promise.when(@call_resource(url, serialised_string)).then (raw_data) ->
      server_data = raw_data[0]
      data = server_data.data
      body = document.getElementsByTagName('body')[0]
      if server_data.status is 'success' and data.status is 3
        data_action = if not partial then \
          'submit' else 'display_partial_reasons'
        can_btn = '<a href="#" data-action="renable" '+
          'data-target="submit_observation">Do not submit</a>'
        act_btn = '<a href="#" data-target="submit_observation" '+
          'data-action="' + data_action + '" data-ajax-action="'+
          data.next_action+'">Submit</a>'
        new window.NH.NHModal('submit_observation',
          server_data.title + ' for ' + self.patient_name() + '?',
          server_data.desc,
          [can_btn, act_btn], 0, body)
        if 'clinical_risk' of data.score
          sub_ob = document.getElementById('submit_observation')
          cls = 'clinicalrisk-'+data.score.clinical_risk.toLowerCase()
          sub_ob.classList.add(cls)
      else if server_data.status is 'success' and data.status is 1
        triggered_tasks = ''
        buttons = ['<a href="'+self.urls['task_list']().url+
          '" data-action="confirm">Go to My Tasks</a>']
        if data.related_tasks.length is 1
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>'
          rt_url = self.urls['single_task'](data.related_tasks[0].id).url
          buttons.push('<a href="'+rt_url+'">Confirm</a>')
        else if data.related_tasks.length > 1
          tasks = ''
          for task in data.related_tasks
            st_url = self.urls['single_task'](task.id).url
            tasks += '<li><a href="'+st_url+'">'+task.summary+'</a></li>'
          triggered_tasks = '<ul class="menu">'+tasks+'</ul>'
        pos = '<p>' + server_data.desc + '</p>'
        os = 'Observation successfully submitted'
        task_list = if triggered_tasks then triggered_tasks else pos
        new window.NH.NHModal('submit_success', server_data.title ,
          task_list, buttons, 0, body)
      else if server_data.status is 'success' and data.status is 4
        triggered_tasks = ''
        buttons = ['<a href="'+self.urls['task_list']().url+
          '" data-action="confirm" data-target="cancel_success">'+
          'Go to My Tasks</a>']
        if data.related_tasks.length is 1
          triggered_tasks = '<p>' + data.related_tasks[0].summary + '</p>'
          rt_url = self.urls['single_task'](data.related_tasks[0].id).url
          buttons.push('<a href="'+rt_url+'">Confirm</a>')
        else if data.related_tasks.length > 1
          tasks = ''
          for task in data.related_tasks
            st_url = self.urls['single_task'](task.id).url
            tasks += '<li><a href="'+st_url+'">'+task.summary+'</a></li>'
          triggered_tasks = '<ul class="menu">'+tasks+'</ul>'
        pos = '<p>' + server_data.desc + '</p>'
        task_list = if triggered_tasks then triggered_tasks else pos
        new window.NH.NHModal('cancel_success', server_data.title,
          task_list, buttons, 0, self.form)
      else
        action_buttons = (element for element in self.form.elements \
          when element.getAttribute('type') in ['submit', 'reset'])
        for button in action_buttons
          button.removeAttribute('disabled')
        btn = '<a href="#" data-action="close" '+
          'data-target="submit_error">Cancel</a>'
        new window.NH.NHModal('submit_error', 'Error submitting observation',
          'Server returned an error', [btn], 0, body)

  display_partial_reasons: (self) =>
    form_type = self.form.getAttribute('data-source')
    observation = self.form.getAttribute('data-type')
    partials_url = @.urls.json_partial_reasons(observation)
    Promise.when(@call_resource(partials_url)).then (rdata) ->
      server_data = rdata[0]
      data = server_data.data
      options = ''
      for option in data
        option_val = option[0]
        option_name = option[1]
        options += '<option value="'+option_val+'">'+option_name+'</option>'
      select = '<select name="partial_reason">'+options+'</select>'
      con_btn = if form_type is 'task' then '<a href="#" ' +
        'data-target="partial_reasons" data-action="partial_submit" '+
        'data-ajax-action="json_task_form_action">Submit</a>'
        else '<a href="#" data-target="partial_reasons" '+
        'data-action="partial_submit" '+
        'data-ajax-action="json_patient_form_action">Submit</a>'
      can_btn = '<a href="#" data-action="renable" '+
        'data-target="partial_reasons">Do not submit</a>'
      msg = '<p>' + server_data.desc + '</p>'
      new window.NH.NHModal('partial_reasons', server_data.title,
        msg+select, [can_btn, con_btn], 0, self.form)


### istanbul ignore if ###
if !window.NH
  window.NH = {}

### istanbul ignore else ###
window?.NH.NHMobileForm = NHMobileFormSLaM

