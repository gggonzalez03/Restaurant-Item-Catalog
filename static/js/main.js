angular.module('catalog', [])
  .controller('CatalogController', function($scope, $http) {
    var catalog = this;
    $scope.restaurant_menu;

    catalog.get_menu_by_restaurant = function(restaurant_id){
    	$http.get("/restaurant/menu/" + restaurant_id)
    	.then(function(data){
    	    $scope.restaurant_menu = data.data;
    	});
    };
  });