
var storageName = "survey-storage"

function loadState(survey) {
    //Here should be the code to load the data from your database
    var storageSt = window
        .sessionStorage
        .getItem(storageName) || "";

    var res = {};
    if (storageSt) 
        res = JSON.parse(storageSt); //Create the survey state for the demo. This line should be deleted in the real app.
    else 
        res = {};

    //Set the loaded data into the survey.
    if (COMPLETED || res.completed) {
        survey.doComplete();
    }
    else if (res.started) {
        // if (res.currentPageNo) 
        survey.start();
        // if (res.data)
        survey.data = res.data;
        survey.currentPageNo = res.currentPageNo;
    }
}

function saveState(survey) {
    var res = {
        started: survey.state == 'running' || survey.state == 'completed',
        completed: survey.state == 'completed',
        currentPageNo: survey.currentPageNo,
        data: survey.data
    };
    //Here should be the code to save the data into your database
    window
        .sessionStorage
        .setItem(storageName, JSON.stringify(res));
}

// Survey.StylesManager.applyTheme("default");
// Survey.StylesManager.applyTheme("modern");
Survey.StylesManager.applyTheme("bootstrap");
// Survey.StylesManager.applyTheme("orange");
// Survey.StylesManager.applyTheme("darkblue");
// Survey.StylesManager.applyTheme("darkrose");
// Survey.StylesManager.applyTheme("stone");
// Survey.StylesManager.applyTheme("winter");
// Survey.StylesManager.applyTheme("winterstone");

// localization
Survey
    .surveyLocalization
    .locales["tr"]["startSurveyText"] = "Başla";

Survey
    .surveyLocalization
    .locales["tr"]["requiredInAllRowsError"] = "Lütfen bütün ifadeleri yanıtla";

Survey.defaultBootstrapCss.navigationButton = 'btn btn-primary';

$.getJSON(JSON_FILE, function (json) {
    window.survey = new Survey.Model(json);

    survey.locale = "tr";

    // survey.maxTimeToFinish = 40 * 60; // 40 min
    // survey.showTimerPanel = "bottom";
    // survey.showTimerPanelMode = "survey";
    survey.firstPageIsStarted = true;
    survey.showPrevButton = false;
    survey.showQuestionNumbers = "false";
    // survey.showProgressBar = false;
    survey.requiredText = "";
    // survey.questionErrorLocation = "bottom";
    
    survey.onValueChanged.add(function (sender, options) {
        saveState(survey);
    });
    
    survey.onCurrentPageChanged.add(function (sender, options) {
        saveState(survey);
    });

    loadState(survey);

    survey.onComplete.add(function (survey, options) {
        $.ajax("submit", {
            data : JSON.stringify(survey.data),
            contentType : 'application/json',
            type : 'POST'
        });
        
        saveState(survey);
    });

    $("#surveyElement").Survey({ 
        model: survey, 
        css: {
            matrix: {
                root: "table table-striped"
            },
            question: {
                title: "question-title",
                content: "q-content"
            },
            page: {
                root: "page-root"
            },
            completedPage : "completed-page",
            html: {
                root: "html-root"
            }
            // ,
            // radiogroup : {
            //     item : "pretty p-default"
            // }
        } 
    });
});
