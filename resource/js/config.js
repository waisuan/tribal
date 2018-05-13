(function (){

    var app = angular.module("tribal");

    app.config(['$locationProvider', function($locationProvider) {
        $locationProvider.hashPrefix('');
    }]);

    app.config(function($routeProvider) {
        $routeProvider.when('/', {
            templateUrl: 'view/form.html',
            controller: 'FormCtrl'
        }).otherwise({
            redirectTo: '/'
        })
    });

})();
