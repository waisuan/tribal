(function (){

    var app = angular.module("tribal");

    app.config(['$locationProvider', function($locationProvider) {
        $locationProvider.html5Mode(true);
    }]);

    app.config(function($routeProvider) {
        $routeProvider.when('/', {
            templateUrl: 'view/form.html',
            controller: 'FormCtrl'
        })
        $routeProvider.when('/admin', {
            templateUrl: 'view/admin.html',
            controller: 'AdminCtrl'
        }).otherwise({
            redirectTo: '/'
        })
    });

})();
