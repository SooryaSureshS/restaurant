odoo.define('school_management_dashboard.SchoolManagementDashboard', function(require) {
    "use strict";
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var SchoolDashboard = AbstractAction.extend({
        template: 'DashboardPropMgt',
        jsLibs: [
            '/school_management_dashboard/static/src/js/plugins/chartJS3_3_2.js',
            '/school_management_dashboard/static/src/js/plugins/googleChart.js',
            '/school_management_dashboard/static/src/js/plugins/jquery.knob.min.js',
            '/school_management_dashboard/static/src/js/plugins/jquery-ui.min.js',
            '/school_management_dashboard/static/src/js/admin_lte/adminlte.js',
        ],
        init: function(parent, context) {
            this._super(parent, context);
        },
        start: function() {
            var self = this;
            this.renderHighFour();
//            this.renderSalesAnalytics();
            this.renderPropertiesOverview();
//            this.renderRentHistory();
            return this._super();
        },
        renderPropertiesOverview(){
            google.charts.load("current", {packages:["corechart"]});
            google.charts.setOnLoadCallback(drawChart);
            function drawChart() {
                var data = google.visualization.arrayToDataTable([
                    ['Type', 'Percentage'],
                    ['Sale',     75],
                    ['Rent',      25]
                ]);
                var options = {
                    is3D: true,
                    legend: 'none',
                    pieSliceText: 'none',
                    backgroundColor: 'F0EFFB',
                    chartArea: {left: 0, top: - 40},
                    colors: ['#2baab6', '#F0B51B'],
                    width: 300
                };
                var chart = new google.visualization.PieChart(document.getElementById('piechart_3d'));
                chart.draw(data, options);
            }
        },
//        renderRentHistory() {
//            google.charts.load('current', {'packages':['corechart']});
//            google.charts.setOnLoadCallback(drawChart);
//            function drawChart() {
//                var data = google.visualization.arrayToDataTable([
//                    ['Month', 'Cost'],
//                    ['April',  200],
//                    ['May',  200],
//                    ['June',  200],
//                    ['July',  200]
//                    ['August',  200]
//                    ['September',  200]
//                    ['October',  200]
//                    ['November',  200k]
//                    ['December',  200]
//                ]);
//                var options = {
//                    title: 'Company Performance',
//                    curveType: 'function',
//                    legend: { position: 'bottom' }
//                };
//                var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));
//                chart.draw(data, options);
//            }
//
//        },
//        renderSalesAnalytics(){
//        var self = this;
//            var donutChartCanvas = self.$('#donutChart').get(0).getContext('2d')
//            var donutData        = {
//                labels: [
//                    'Online Sales',
//                    'Offline Sales',
//                    'Agent Sales',
//                    'Marketing Sales',
//                ],
//                datasets: [
//                    {
//                        data: [700,500,400,600],
//                        backgroundColor : ['#79D439', '#2baab6', '#ED8A23', '#F0B51B'],
//                    }
//                ],
//            }
//            var donutOptions     = {
//                maintainAspectRatio : false,
//                responsive : true,
//                cutout: '70%',
//                elements: {
//                    arc: {
//                        borderColor: '#F0EFFB',
//                        borderWidth: 5,
//                        borderRadius: 3,
//                    }
//                },
//                plugins : {
//                    legend: {
//                      display: false,
//                    }
//                }
//            }
//            //Create pie or douhnut chart
//            // You can switch between pie and douhnut using the method below.
//            new Chart(donutChartCanvas, {
//                type: 'doughnut',
//                data: donutData,
//                options: donutOptions
//            })
//        },
        renderHighFour(){
            console.log('renderHighFour>>>>>>>>>>>>>>>>>>>>>>>>')
            var self = this;
            self.$('.knob').knob({
                draw: function () {
                    // "tron" case
                    if (this.$.data('skin') == 'tron') {
                        var a   = this.angle(this.cv),  // Angle
                        sa  = this.startAngle,          // Previous start angle
                        sat = this.startAngle,          // Start angle
                        ea,                             // Previous end angle
                        eat = sat + a,                  // End angle
                        r   = true
                        this.g.lineWidth = this.lineWidth
                        this.o.cursor
                        && (sat = eat - 0.3)
                        && (eat = eat + 0.3)
                        if (this.o.displayPrevious) {
                            ea = this.startAngle + this.angle(this.value)
                            this.o.cursor
                            && (sa = ea - 0.3)
                            && (ea = ea + 0.3)
                            this.g.beginPath()
                            this.g.strokeStyle = this.previousColor
                            this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sa, ea, false)
                            this.g.stroke()
                        }
                        this.g.beginPath()
                        this.g.strokeStyle = r ? this.o.fgColor : this.fgColor
                        this.g.arc(this.xy, this.xy, this.radius - this.lineWidth, sat, eat, false)
                        this.g.stroke()
                        this.g.lineWidth = 2
                        this.g.beginPath()
                        this.g.strokeStyle = this.o.fgColor
                        this.g.arc(this.xy, this.xy, this.radius - this.lineWidth + 1 + this.lineWidth * 2 / 3, 0, 2 * Math.PI, false)
                        this.g.stroke()
                        return false
                    }
                }
            })
        }
    });

    core.action_registry.add('school_management_dashboard', SchoolDashboard);
    return SchoolDashboard;
    });
