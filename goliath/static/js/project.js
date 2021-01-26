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

function setupSurvey(casetypeId, surveyJSON, csrfToken, newUser) {
  if (newUser) surveyJSON = addUserToJson(surveyJSON);

  function sendDataToServer(survey, options) {
    if (options.isCompleteOnTrigger) {
      alert("Please do something else");
      window.location.replace("/neu/");
      return;
    }

    // jQuery does some wild preprocessing with JSONs so turn it into string
    var body = {
      answers: JSON.stringify(survey.data),
      text: window.finalText,
      csrfmiddlewaretoken: csrfToken,
    };

    $.post("/neu/" + casetypeId + "/", body)
      .done(function (successData) {
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
      $(".aw-completebutton").removeClass("aw-hidden");
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
  window.isCompleting = false;
  function beforeComplete() {
    window.isCompleting = true;
    return true;
  }

  var surveyValueChanged = function (sender, options) {
    if (options.name != "previewhtml" && window.isCompleting === false) {
      window.finalText = constructLetterText();
      window.awsurvey.getQuestionByName("previewhtml").html =
        "<div class='previewhtml'><h2>Vorschau</h2>" +
        "<p>" +
        window.finalText +
        "</p></div>";
    }

    var el = document.getElementById(options.name);
    if (el) {
      el.value = options.value;
    }
  };

  // not using default theme right now

  // var defaultThemeColors = Survey.StylesManager.ThemeColors["default"];
  // defaultThemeColors["$main-color"] = "#1f9bcc";
  // defaultThemeColors["$main-hover-color"] = "#1f9bcc";
  // defaultThemeColors["$text-color"] = "#4a4a4a";
  // defaultThemeColors["$header-color"] = "#7ff07f";

  // defaultThemeColors["$header-background-color"] = "#4a4a4a";
  // defaultThemeColors["$body-container-background-color"] = "#f8f8f8";

  // Survey.StylesManager.applyTheme();

  var survey = new Survey.Model(surveyJSON);

  survey.locale = "de";
  // survey.showProgressBar = "top";
  // survey.showPageNumbers = true;
  // survey.showTitle = false;
  survey.showPreviewBeforeComplete = true;
  survey.completedHtml = "<p>Bitte einen kurzen Augenblick warten...</p>";

  // https://surveyjs.io/Documentation/Library?id=SurveyModel#questionsOnPageMode
  survey.questionsOnPageMode = "singlePage";

  // ensure deleting all values when
  survey.clearInvisibleValues = "onHidden";

  survey.completeText = "Anliegen melden & versenden";

  window.awsurvey = survey;

  // what classes to customize
  // https://surveyjs.io/Examples/Library/?id=survey-customcss&platform=jQuery&theme=modern#content-docs

  $(".survey-inner").Survey({
    model: window.awsurvey,
    onAfterRenderQuestion: afterRenderQuestion,
    onComplete: sendDataToServer,
    onCompleting: beforeComplete,
    onValueChanged: surveyValueChanged,
    css: {
      navigation: { complete: "btn aw-hidden aw-completebutton" },
      question: {
        mainRoot: "sv_q sv_qstn fade-in",
      },
    },
  });
}

window.setupSurvey = setupSurvey;
