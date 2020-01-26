
// Survey.StylesManager.applyTheme("default");
// Survey.StylesManager.applyTheme("modern");
Survey.StylesManager.applyTheme("bootstrap");
// Survey.StylesManager.applyTheme("orange");
// Survey.StylesManager.applyTheme("darkblue");
// Survey.StylesManager.applyTheme("darkrose");
// Survey.StylesManager.applyTheme("stone");
// Survey.StylesManager.applyTheme("winter");
// Survey.StylesManager.applyTheme("winterstone");


Survey.defaultBootstrapCss.navigationButton = 'btn btn-primary';

$.getJSON("survey.json", function (json) {
    window.survey = new Survey.Model(json);

    survey.maxTimeToFinish = 40 * 60; // 40 min
    // survey.showTimerPanel = "bottom";
    survey.showTimerPanelMode = "survey";
    survey.firstPageIsStarted = true;
    survey.showPrevButton = false;
    survey.showQuestionNumbers = "false";
    survey.showProgressBar = "true";
    survey.requiredText = "";

    survey.onComplete.add(function (result) {
        $.ajax("update", {
            data : JSON.stringify(result.data),
            contentType : 'application/json',
            type : 'POST'
        });
        // document.querySelector("#surveyResult").textContent =
        //     "Result JSON:\n" + JSON.stringify(result.data, null, 3);
    });

    // var radio_div = document.getElementById("pretty-checkbox")

    // survey.onAfterRenderPage.add(function(survey, options) {

    //     // var radios = options.htmlElement.querySelectorAll('input[type="radio"]');

    //     // for (let radio of radios) {
    //     //     var div = document.createElement("div");
    //     //     div.classList.add("pure-radiobutton");
    //     //     radio.replaceWith(div);
    //     //     div.appendChild(radio);
    //     // }

    //     $('input[type="radio"]').iCheck({
    //         labelHover: false,
    //         cursor: true
    //     });
    // });

    

    $("#surveyElement").Survey({ 
        model: survey, 
        css: {
            matrix: {
                root: "table table-striped"
            },
            question: {
                content: "q-content"
            }
            // ,
            // radiogroup : {
            //     item : "pretty p-default"
            // }
        } 
    });
});
