(function (){

    var app = angular.module("tribal");

    app.controller('AdminCtrl', function($scope, $http, $timeout) {
        $scope.data = { 'title': '', 'message': '', 'attachment': '' };
        $scope.success = false;
        $scope.failure = false;
        $scope.submitting = false;
        $scope.empty = false;

        $scope.submit = function() {
            if (!$scope.data['attachment']) {
                $scope.empty = true;
                $timeout(function() {
                    $scope.empty = false;
                }, 1000);
                return;
            }

            var payload = new FormData();
            payload.append('title',      $scope.data['title']);
            payload.append('message',    $scope.data['message']);
            payload.append('attachment', $scope.data['attachment']);

            $scope.success = false;
            $scope.failure = false;
            $scope.submitting = true;
            $http.post('/admin', payload, { transformRequest: angular.identity,
                                            headers: {'Content-Type': undefined}
                                        }).then(function(data) {
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
