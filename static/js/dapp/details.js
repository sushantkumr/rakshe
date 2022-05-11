$(document).ready(function() {
    var ctx = $("#myChart");

    function DappDetailsViewModel() {
        var self = this;
        self.name = ko.observable('Etheroll');
        self.contracts = ko.observableArray([1, 2]);
        self.website = ko.observable('http://example.com');

        self.rawUsageData = ko.observableArray();
    }

    _dappDetailsViewModel = new DappDetailsViewModel();
    ko.applyBindings(_dappDetailsViewModel);
    // $('#js--developer-new_application').addClass('active');

    var dappId = ec.utils.getQueryStringValue('dappId');

    if (!dappId) {
        ec.utils.bootboxError('A DApp id was not found.');
        return;
    }

    ec.utils.eajax('list_dapp', 'views', 'get_dapp_usage_data', {dapp_id: dappId}, function(response) {
        window.r = response;
        if (!response.success) {
            ec.utils.bootboxError(response);
            return;
        }

        var chartOptions = {
            scales: {
                yAxes: [{
                    id: 'gasConsumption',
                    type: 'linear',
                    position: 'left'
                }, {
                    id: 'numberOfPolicies',
                    type: 'linear',
                    position: 'right'
                }],
                xAxes: [{
                    ticks: {
                        // autoSkip: true,
                        // maxTicksLimit: 10
                    }
                }]
            },
            elements: {
                point: {
                    radius: 1
                }
            },
            animation: {
                duration: 3000, // general animation time
            },
            hover: {
                animationDuration: 0, // duration of animations when hovering an item
            },
            responsiveAnimationDuration: 0, // animation duration after a resize
        };

        var usageChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: response.data.labels,
                datasets: [{
                    label: 'Gas Consumption',
                    data: response.data.gasUsed,
                    yAxisID: 'gasConsumption',
                    borderColor: '#78aa50',
                    backgroundColor: 'rgba(204, 204, 204, 0.4)',
                    borderWidth: 1.5,
                }, {
                    label: 'Number of Policies (Fake data)',
                    data: response.data.txCount,
                    yAxisID: 'numberOfPolicies',
                    borderColor: 'red',
                    backgroundColor: 'rgba(204, 204, 204, 0.4)',
                    borderWidth: 1.5,
                }]
            },
            options: chartOptions
        });
    });
});
