function setupSurvey(casetypeId, surveyJSON, csrfToken) {
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
          sendDataToServer(survey);
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
    setTimeout(
      () =>
        options.htmlElement.scrollIntoView({
          behavior: "smooth",
          block: "end",
          inline: "end",
        }),
      100
    );
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
        "<h1>Vorschau</h1>" + "<p>" + window.finalText + "</p>";
    }

    var el = document.getElementById(options.name);
    if (el) {
      el.value = options.value;
    }
  };

  var defaultThemeColors = Survey.StylesManager.ThemeColors["default"];
  defaultThemeColors["$main-color"] = "#1f9bcc";
  defaultThemeColors["$main-hover-color"] = "#1f9bcc";
  // defaultThemeColors["$text-color"] = "#4a4a4a";
  // defaultThemeColors["$header-color"] = "#7ff07f";

  // defaultThemeColors["$header-background-color"] = "#4a4a4a";
  // defaultThemeColors["$body-container-background-color"] = "#f8f8f8";

  Survey.StylesManager.applyTheme();

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

  window.awsurvey = survey;

  // what classes to customize
  // https://surveyjs.io/Examples/Library/?id=survey-customcss&platform=jQuery&theme=modern#content-docs

  $("#survey-container").Survey({
    model: window.awsurvey,
    onAfterRenderQuestion: afterRenderQuestion,
    onComplete: sendDataToServer,
    onCompleting: beforeComplete,
    onValueChanged: surveyValueChanged,
    css: {
      question: { mainRoot: "sv_q sv_qstn fade-in" },
    },
  });
}

window.setupSurvey = setupSurvey;
