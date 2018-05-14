(function (){

    var app = angular.module("tribal");

    app.config(['$locationProvider', function($locationProvider) {
        $locationProvider.hashPrefix('');
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
