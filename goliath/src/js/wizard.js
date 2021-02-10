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

function setupSurvey(casetypeId, surveyJSON, csrfToken, newUser) {
  if (newUser) surveyJSON = addUserToJson(surveyJSON);

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

  function constructLetterText() {
    var text = "";
    var values = window.awsurvey.getPlainData();
    for (var i = 0; i < values.length; i++) {
      if (values[i].value != null) text += values[i].value + " ";
    }
    return text;
  }

  function afterRenderQuestion(sender, options) {
    // make button visibile when preview gets rendered
    if (options.question.name === "previewhtml") {
      $(".aw-completebutton").removeClass("hidden");
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
      window.awsurvey.getQuestionByName("previewhtml").html =
        "<div class='previewhtml'><h2>Vorschau</h2>" +
        "<div><p>" +
        window.awfinalText +
        "</p></div><div><p>Wenn Sie auf Abschließen clicken, passiert das und das.</p></div></div>";
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
