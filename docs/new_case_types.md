# How to create new case types for dataskop

Go to <https://surveyjs.io/create-survey> and create your survey.
You need to copy out the JSON and insert it into dataskop case type question field.

The pages are responsible for adding a progress bar.
You can use the logic of surveyjs.

As the last page, add a page with a single html element.
The name of this html element has to be `previewhtml`.

To formulate the text of the message, use hidden elements for e.g. the start and/or end of the letter. This is always the same.
Or add the texts as values to the questions. Those values are then picked to construct the final text.

You can use the logic of surveyjs to hide / show certain other questions.
But if you change the values of items of a question, ensure you change the value in the logic as well.

(This description needs to get improved.)
