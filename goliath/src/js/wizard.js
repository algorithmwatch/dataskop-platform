import * as $ from "jquery";
import * as Survey from "survey-jquery";

// export for others scripts to use
window.$ = $;

function addUserToJson(surveyJSON) {
  var lastPageIndex = surveyJSON.pages.length - 1;
  var lastPage = surveyJSON.pages[lastPageIndex];
  var previewhtmlElement = lastPage.elements[0];

  var firstNameQuestion = {
    visible: false,
    type: "text",
    name: "awfirstnamequestion",
    title: "Wie ist dein Vorname?",
    visibleIf: previewhtmlElement.visibleIf,
  };

  var lastNameQuestion = {
    visible: false,
    type: "text",
    name: "awlastnamequestion",
    title: "Wie ist dein Nachname?",
    visibleIf: "{awfirstnamequestion} notempty",
  };

  var emailQuestion = {
    visible: false,
    type: "text",
    name: "awemailquestion",
    title: "Wie ist dein E-Mail-Adresse?",
    visibleIf: "{awlastnamequestion} notempty",
    validators: [
      {
        type: "email",
      },
    ],
  };

  previewhtmlElement.visibleIf = "{awemailquestion} notempty";

  surveyJSON.pages[lastPageIndex].elements = [
    firstNameQuestion,
    lastNameQuestion,
    emailQuestion,
    previewhtmlElement,
  ];
  return surveyJSON;
}

function addEntityChooseToJson(surveyJSON, entities) {
  var entityQuestion = {
    type: "checkbox",
    choices: entities.map((x) => {
      return { value: x[0], text: x[1] };
    }),
    visible: true,
    name: "awentitycheckbox",
    title: "An wen richtet sich die Anfrage?",
  };

  // search for first visible question, hide it, make it visible when
  // entity choosing was done
  for (let i = 0; i < surveyJSON.pages[0].elements.length; i++) {
    let x = surveyJSON.pages[0].elements[i];
    if (!("visible" in x) || x.visible) {
      x.visible = false;
      x.visibleIf = "{awentitycheckbox} notempty";
      break;
    }
  }

  surveyJSON.pages[0].elements.unshift(entityQuestion);
  return surveyJSON;
}

// via https://surveyjs.io/Examples/Library?id=survey-editprevious&platform=jQuery&theme=modern#content-js
// save storage with specific name of case id
function Storage(storageName) {
  function loadState(survey) {
    var storageSt = window.localStorage.getItem(storageName) || "";
    var res = {};
    if (storageSt) res = JSON.parse(storageSt);

    if (res.data) survey.data = res.data;
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

function setupSurvey(casetypeId, surveyJSON, csrfToken, userName, entities) {
  if (userName === null) surveyJSON = addUserToJson(surveyJSON);
  if (entities.length > 1)
    surveyJSON = addEntityChooseToJson(surveyJSON, entities);

  window.awstorage = Storage("aw-goliath-storage-" + casetypeId);

  function sendDataToServer(survey, options) {
    if (options.isCompleteOnTrigger) {
      alert("Please do something else");
      window.location.replace("/neu/");
      return;
    }

    // jQuery does some wild preprocessing with JSONs so turn it into string
    var body = {
      answers: JSON.stringify(survey.data),
      text: window.awfinalText,
      csrfmiddlewaretoken: csrfToken,
    };

    $.post("/neu/" + casetypeId + "/", body)
      .done(function (successData) {
        window.awstorage.removeState();
        window.location.replace(successData.url);
      })
      .fail(function () {
        alert("error");
        setTimeout(function () {
          sendDataToServer(survey, options);
        }, 1000);
      });
  }

  const constructLetterText = (function (userName) {
    return function () {
      var text = "Sehr geehrte Damen und Herren,\n\n";
      var context = {};
      var values = window.awsurvey.getPlainData();
      // user name was provided by the setupSurvey
      for (var i = 0; i < values.length; i++) {
        if (values[i].name == "awfirstnamequestion") {
          userName = values[i].value;
          continue;
        }

        if (values[i].name == "awlastnamequestion") {
          userName += " " + values[i].value;
          continue;
        }

        if (["awemailquestion", "awentitycheckbox"].includes(values[i].name))
          continue;

        if (values[i].value != null) {
          context[values[i].name] = values[i].value;
        }
      }

      var template = Handlebars.compile(
        window.awsurvey.getQuestionByName("previewhtml").html
      );
      text += template(context);
      text += "\nMit freudlichen Grüßen\n\n" + userName;
      return text;
    };
  })(userName);

  function afterRenderQuestion(sender, options) {
    // make button visibile when preview gets rendered
    if (options.question.name === "previewhtml") {
      $(".aw-completebutton").removeClass("hidden");
    }

    var questionType = options.question.getType();

    // remove previously added next button
    $(".aw-survey-next-button").remove();
    if (questionType === "text") {
      // add next button
      $(options.htmlElement).append(
        '<div class="text-right clear-both aw-survey-next-button"><btn class="btn btn--regular btn--primary">weiter</btn></div>'
      );
    }

    setTimeout(function () {
      options.htmlElement.scrollIntoView({
        behavior: "smooth",
        block: "end",
        inline: "end",
      });
    }, 100);
    setTimeout(function () {
      $(options.htmlElement).find("input").focus();
      options.htmlElement.focus();
    }, 150);
  }

  // survejs changed the values right before completing.
  // So check if the complete button was clicked to prevent chaning the preview text ect.
  window.awisCompleting = false;
  function beforeComplete() {
    window.awisCompleting = true;
    return true;
  }

  function surveyValueChanged(sender, options) {
    if (options.name != "previewhtml" && window.awisCompleting === false) {
      window.awfinalText = constructLetterText();
      console.log(window.awfinalText);
    }
    var el = document.getElementById(options.name);
    if (el) {
      el.value = options.value;
    }
  }

  // setting up the survey & setting some appropiate values
  var survey = new Survey.Model(surveyJSON);
  survey.locale = "de";
  survey.showPreviewBeforeComplete = true;
  survey.completedHtml = "<p>Bitte einen kurzen Augenblick warten...</p>";
  survey.completeText = "Abschließen";

  // https://surveyjs.io/Documentation/Library?id=SurveyModel#questionsOnPageMode
  survey.questionsOnPageMode = "singlePage";

  // ensure deleting all values when changing a value further below
  survey.clearInvisibleValues = "onHidden";

  // persist state every time a new question gets rendered
  survey.onAfterRenderQuestion.add(function (survey, options) {
    window.awstorage.saveState(survey);
  });

  window.awsurvey = survey;

  // load the initial state if available
  // TODO: if the survey was almost complete, the previewtext + button are not shown
  window.awstorage.loadState(window.awsurvey);

  // what classes to customize
  // https://surveyjs.io/Examples/Library/?id=survey-customcss&platform=jQuery&theme=modern#content-docs

  $(".survey-reset").click(() => {
    window.awstorage.removeState();
    location.reload();
  });

  $(".survey-inner").Survey({
    model: window.awsurvey,
    onAfterRenderQuestion: afterRenderQuestion,
    onComplete: sendDataToServer,
    onCompleting: beforeComplete,
    onValueChanged: surveyValueChanged,
    css: {
      navigation: { complete: "btn--primary hidden aw-completebutton" },
    },
  });
}

window.setupSurvey = setupSurvey;
