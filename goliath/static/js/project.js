/* Project specific Javascript goes here. */

function setupSurvey(casetypeId, surveyJSON, csrfToken) {
  function sendDataToServer(survey) {
    // jQuery does some wild preprocessing with JSONs so turn it into string
    var body = {
      answers: JSON.stringify(survey.data),
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

  // Survey.StylesManager.applyTheme("modern");
  // Survey.StylesManager.applyTheme("bootstrap");

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
  survey.showProgressBar = "top";
  survey.showPageNumbers = true;
  survey.showTitle = false;
  survey.completedHtml = "<p>Bitte einen kurzen Augenblick warten...</p>";

  $("#survey-container").Survey({
    model: survey,
    onComplete: sendDataToServer,
    css: {
      navigationButton: "button btn-primary",
    },
  });
}

window.setupSurvey = setupSurvey;
