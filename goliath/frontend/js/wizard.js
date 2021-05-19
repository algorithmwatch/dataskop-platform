import * as $ from 'jquery';
import * as Survey from 'survey-jquery';

// export for others scripts to use
window.$ = $;

function addUserToJson(surveyJSON) {
  var lastPageIndex = surveyJSON.pages.length - 1;
  var lastPage = surveyJSON.pages[lastPageIndex];
  var previewhtmlElement = lastPage.elements[0];

  var firstNameQuestion = {
    visible: false,
    type: 'text',
    name: 'awfirstnamequestion',
    title:
      'Ihr Vor- und Nachname wird zur Unterzeichnung der E-Mail an das Unternehmen/die Behörde verwendet. Wir empfehlen, Ihren Klarnamen zu verwenden. Wie ist Ihr Vorname?',
    visibleIf: previewhtmlElement.visibleIf,
  };

  var lastNameQuestion = {
    visible: false,
    type: 'text',
    name: 'awlastnamequestion',
    title: 'Wie ist Ihr Nachname?',
    visibleIf: '{awfirstnamequestion} notempty',
  };

  var emailQuestion = {
    visible: false,
    type: 'text',
    name: 'awemailquestion',
    title: 'Wie ist Ihre E-Mail-Adresse?',
    visibleIf: '{awlastnamequestion} notempty',
    validators: [
      {
        type: 'email',
      },
    ],
  };

  previewhtmlElement.visibleIf = '{awemailquestion} notempty';

  surveyJSON.pages[lastPageIndex].elements = [
    firstNameQuestion,
    lastNameQuestion,
    emailQuestion,
    previewhtmlElement,
  ];
  return surveyJSON;
}

function getQuestionType(questionOptions, surveyJSON) {
  const type = questionOptions.question.getType();
  const name = questionOptions.htmlElement.name;
  let inputType = null;
  surveyJSON.pages.forEach((page) => {
    page.elements.forEach((ele) => {
      if (ele.name === name && 'inputType' in ele) {
        inputType = ele.inputType;
      }
    });
  });
  return [type, inputType];
}

function addEntityChooseToJson(surveyJSON, chooseEntities) {
  var entityQuestion = {
    type: 'checkbox',
    choices: chooseEntities.map((x) => {
      return { value: x[0], text: x[1] };
    }),
    visible: true,
    name: 'awentitycheckbox',
    title: 'An wen richtet sich die Anfrage?',
  };

  // search for first visible question, hide it, make it visible when
  // entity choosing was done
  for (let i = 0; i < surveyJSON.pages[0].elements.length; i++) {
    let x = surveyJSON.pages[0].elements[i];
    if (!('visible' in x) || x.visible) {
      x.visible = false;
      x.visibleIf = '{awentitycheckbox} notempty';
      break;
    }
  }

  surveyJSON.pages[0].elements.unshift(entityQuestion);
  return surveyJSON;
}

function addAdditionalProps(surveyJSON) {
  const pages = surveyJSON.pages;

  for (let i = 0, l = pages.length; i < l; i++) {
    const elements = pages[i].elements;
    if (elements) {
      for (let x = 0, l2 = elements.length; x < l2; x++) {
        elements[x].minWidth = '0';
        elements[x].size = '';
      }
    }
  }

  return surveyJSON;
}

// via https://surveyjs.io/Examples/Library?id=survey-editprevious&platform=jQuery&theme=modern#content-js
// save storage with specific name of case id
function Storage(storageName) {
  function loadState(survey) {
    var storageSt = window.localStorage.getItem(storageName) || '';
    var res = {};
    if (storageSt) res = JSON.parse(storageSt);

    if (res.data) {
      survey.data = res.data;
    }
  }

  function saveState(survey) {
    var res = {
      data: survey.data,
    };
    window.localStorage.setItem(storageName, JSON.stringify(res));
  }

  function removeState() {
    window.localStorage.removeItem(storageName);
  }
  return {
    loadState,
    saveState,
    removeState,
  };
}

function getAnswers() {
  var context = {};
  var values = window.awsurvey.getPlainData();
  // user name was provided by the setupSurvey
  for (var i = 0; i < values.length; i++) {
    // if (values[i].name == "awfirstnamequestion") {
    //   userName = values[i].value;
    //   continue;
    // }

    // if (values[i].name == "awlastnamequestion") {
    //   userName += " " + values[i].value;
    //   continue;
    // }

    // if (["awemailquestion", "awentitycheckbox"].includes(values[i].name))
    //   continue;

    if (values[i].value != null) {
      context[values[i].name.replace('-', '_')] =
        values[i].displayValue || values[i].value;
    }
  }

  return context;
}

// radio groups with a single item: a next button, make them visually identical to other next buttons
function chanageToNextButton(element) {
  const children = $(element).find('.wizard-radio-label');
  if (children.length !== 1) return;
  // there is only one radio group icon

  // but is a next button
  const childrenSpan = $(element).find(
    ".wizard-radio-label span[title='weiter']"
  );
  if (childrenSpan.length !== 1) return;

  children.removeClass('wizard-radio-label');
  childrenSpan.addClass('btn btn--regular btn--primary aw-survey-next-button');
}

function setupSurvey(
  casetypeSlug,
  casetypeId,
  surveyJSON,
  csrfToken,
  userName,
  chooseEntities,
  endpoint,
  renderPreviewText
) {
  if (userName === null) surveyJSON = addUserToJson(surveyJSON);
  // currently not needed
  if (chooseEntities.length > 1)
    surveyJSON = addEntityChooseToJson(surveyJSON, chooseEntities);

  surveyJSON = addAdditionalProps(surveyJSON);

  window.awstorage = Storage('aw-goliath-storage-' + casetypeId);

  function sendDataToServer(survey, options) {
    if (options.isCompleteOnTrigger) {
      alert('Please do something else');
      window.location.replace(endpoint);
      return;
    }

    // jQuery does some wild preprocessing with JSONs so turn it into string
    var body = {
      answers: JSON.stringify(getAnswers()),
      csrfmiddlewaretoken: csrfToken,
    };

    $.post(endpoint + casetypeSlug + '/' + casetypeId + '/', body)
      .done(function (successData) {
        window.awstorage.removeState();
        window.location.replace(successData.url);
      })
      .fail(function () {
        alert('error');
        setTimeout(function () {
          sendDataToServer(survey, options);
        }, 1000);
      });
  }

  const completeText =
    'Wenn Sie "Abschließen" wählen, wird dieses Schreiben in Ihrem Namen übermittelt. Wir schicken Ihnen dann eine Bestätigung per E-Mail. Gegebenenfalls müssen Sie noch Ihre Anmeldung bei Unding bestätigen. Bitte schauen Sie dafür in Ihr E-mail-Postfach.';

  const constructLetterText = (function (userName, casetypeId) {
    return function () {
      const context = getAnswers();
      var body = {
        answers: JSON.stringify(context),
        username: userName,
      };

      $.post('/falltyp-text/' + casetypeId + '/', body).done(function (
        successData
      ) {
        window.awsurvey.getQuestionByName('previewhtml').html =
          "<div class='previewhtml'><div class='hl-lg mt-4 mb-2 ml-4'>Vorschau:</div>" +
          "<div><p class='whitespace-pre-wrap rounded-xl border-2 border-dashed border-orange-200 bg-white px-4 py-5 md:py-6 md:px-6 font-serif'>" +
          successData +
          "</p></div><div><p class='mt-4 ml-4'>" +
          completeText +
          '</p></div></div>';
      });
    };
  })(userName, casetypeId);

  function afterRenderQuestion(sender, options) {
    // make button visibile when preview gets rendered
    // but only if we have the preview text to confirm
    if (options.question.name === 'previewhtml') {
      if (renderPreviewText) $('.aw-completebutton').removeClass('hidden');
      else $('.aw-completebutton').click();
    }

    const [questionType, questionInputType] = getQuestionType(
      options,
      surveyJSON
    );

    // remove previously added next button
    $('.aw-survey-next-button').parents('.wizard-answers-container').remove();
    $('.aw-survey-next-button').remove();

    if (
      questionType === 'text' &&
      (questionInputType === null || questionInputType !== 'date')
    ) {
      // add next button
      $(options.htmlElement).append(
        '<div class="mt-4 text-right clear-both aw-survey-next-button"><button type="button" class="btn btn--regular btn--primary">weiter</button></div>'
      );
    }

    if (questionType == 'radiogroup') {
      chanageToNextButton(options.htmlElement);
    }

    if (!window.awDontScroll) {
      setTimeout(function () {
        options.htmlElement.scrollIntoView({
          behavior: 'smooth',
          block: 'end',
          inline: 'end',
        });
      }, 100);
      setTimeout(function () {
        $(options.htmlElement).find('input').focus();
        options.htmlElement.focus();
      }, 150);
    }
  }

  // survejs changed the values right before completing.
  // So check if the complete button was clicked to prevent chaning the preview text ect.
  window.awisCompleting = false;
  function beforeComplete() {
    window.awisCompleting = true;
    return true;
  }

  function surveyValueChanged(sender, options) {
    if (
      options.name != 'previewhtml' &&
      window.awisCompleting === false &&
      renderPreviewText
    ) {
      constructLetterText();
    }
    var el = document.getElementById(options.name);
    if (el) {
      el.value = options.value;
    }

    const questionType = options.question.getType();

    if (questionType == 'radiogroup') {
      // remove non-checked values only for radio groups
      const $el = $('#' + options.question.id);
      $el.find('.sv-q-col-1').not('.checked').remove();
    }

    if (questionType == 'checkbox') {
      window.awDontScroll = true;
    } else {
      window.awDontScroll = false;
    }
  }

  // setting up the survey & setting some appropiate values
  var survey = new Survey.Model(surveyJSON);
  survey.locale = 'de';
  survey.showPreviewBeforeComplete = true;
  survey.completedHtml = '<p>Bitte einen kurzen Augenblick warten...</p>';
  survey.completeText = 'Abschließen';
  survey.showQuestionNumbers = 'off';

  // https://surveyjs.io/Documentation/Library?id=SurveyModel#questionsOnPageMode
  survey.questionsOnPageMode = 'singlePage';

  // ensure deleting all values when changing a value further below
  survey.clearInvisibleValues = 'onHidden';

  // persist state every time a new question gets rendered
  survey.onAfterRenderQuestion.add(function (survey, options) {
    window.awstorage.saveState(survey);
  });

  window.awsurvey = survey;

  // load the initial state if available
  // TODO: if the survey was almost complete, the previewtext + button are not shown
  // window.awstorage.loadState(window.awsurvey);

  // what classes to customize
  // https://surveyjs.io/Examples/Library/?id=survey-customcss&platform=jQuery&theme=modern#content-docs

  $('.survey-reset').click(() => {
    window.awstorage.removeState();
    location.reload();
  });

  $('.survey-inner').Survey({
    model: window.awsurvey,
    onAfterRenderQuestion: afterRenderQuestion,
    onComplete: sendDataToServer,
    onCompleting: beforeComplete,
    onValueChanged: surveyValueChanged,
    css: {
      navigation: {
        complete: 'btn btn--primary btn--regular hidden aw-completebutton',
      },
      row: 'wizard-row',
      question: {
        mainRoot: 'wizard-question-container',
        // "flowRoot": "sv_q_flow sv_qstn",
        header: 'wizard-question',
        // "headerLeft": "title-left",
        content: 'wizard-answers-container',
        // "contentLeft": "content-left",
        // "titleLeftRoot": "sv_qstn_left",
        // "title": "",
        // "titleExpandable": "sv_q_title_expandable",
        // "number": "sv_q_num",
        // "description": "small",
        // "descriptionUnderInput": "small",
        // "requiredText": "sv_q_required_text",
        // "comment": "form-control",
        // "required": "",
        // "titleRequired": "",
        // "hasError": "has-error",
        // "indent": 20,
        // "formGroup": "form-group"
      },
      panel: {
        // "title": "sv_p_title",
        // "titleExpandable": "sv_p_title_expandable",
        // "titleOnError": "",
        // "icon": "sv_panel_icon",
        // "iconExpanded": "sv_expanded",
        container: 'wizard-container',
        // "footer": "sv_p_footer",
        // "number": "sv_q_num",
        // "requiredText": "sv_q_required_text"
      },
      checkbox: {
        // root: 'sv_qcbc sv_qcbx form-inline',
        // item: 'checkbox',
        // itemChecked: 'checked',
        // itemSelectAll: 'sv_q_checkbox_selectall',
        // itemNone: 'sv_q_checkbox_none',
        // itemInline: 'sv_q_checkbox_inline',
        itemControl: 'wizard-radio-button',
        // // itemDecorator: 'sv-hidden',
        label: 'wizard-radio-label',
        labelChecked: 'wizard-radio-group-checked',
        // controlLabel: '',
        // materialDecorator: 'checkbox-material',
        // other: 'sv_q_checkbox_other form-control',
        // column: 'sv_q_select_column',
      },
      radiogroup: {
        // "root": "sv_qcbc form-inline",
        // "item": "radio",
        // "itemChecked": "checked",
        // "itemInline": "sv_q_radiogroup_inline",
        label: 'wizard-radio-label',
        labelChecked: 'wizard-radio-group-checked',
        itemControl: 'wizard-radio-button',
        // "itemDecorator": "sv-hidden",
        // "controlLabel": "testclass3",
        // "materialDecorator": "circle",
        // "other": "sv_q_radiogroup_other form-control",
        // "clearButton": "sv_q_radiogroup_clear button",
        // "column": "sv_q_select_column"
      },
    },
  });
}

window.setupSurvey = setupSurvey;
