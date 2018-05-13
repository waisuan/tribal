(function (){

    var app = angular.module("tribal");

    app.controller('FormCtrl', function($scope, $http, $timeout) {
        $scope.data = { 'name': '', 'email': ''};
        $scope.success = false;
        $scope.failure = false;
        $scope.submitting = false;

        $scope.submit = function() {
            $scope.success = false;
            $scope.failure = false;
            $scope.submitting = true;
            $http.post('/', $scope.data).then(function(data) {
                $timeout(function(){
                    $scope.success = true;
                    $scope.submitting = false;
                }, 500);
            }).catch(function(response) {
                console.error(response.status, response.data);
                $timeout(function(){
                    $scope.failure = true;
                    $scope.submitting = false;
                }, 500);
            })
        }
    });

})();
