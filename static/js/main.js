angular.module('catalog', [])
  .controller('CatalogController', function($scope, $http) {
    var catalog = this;
    $scope.restaurant_menu;
    $scope.is_owned;

    catalog.get_menu_by_restaurant = function(restaurant_id){
    	$http.get("/restaurant/menu/" + restaurant_id)
    	.then(function(data){
    	    $scope.restaurant_menu = data.data.results;
    	});
    };

    catalog.is_item_owned = function(item_id){
    	$http.get("/restaurant/menu/" + item_id + "/isowned")
    	.then(function(data){
    	    $scope.is_owned = data.data.results[0].answer;
    	});
    };
  });