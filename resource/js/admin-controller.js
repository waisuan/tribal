(function (){

    var app = angular.module("tribal");

    app.controller('AdminCtrl', function($scope, $http, $timeout) {
        $scope.data = { 'title': '', 'message': '', 'attachment': '' };
        $scope.success = false;
        $scope.failure = false;
        $scope.submitting = false;
    });

})();
