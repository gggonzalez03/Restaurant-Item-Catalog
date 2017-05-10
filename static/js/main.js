angular.module('catalog', [], function($interpolateProvider) {
    $interpolateProvider.startSymbol('[{');
    $interpolateProvider.endSymbol('}]');
})
  .controller('CatalogController', function($scope, $http, $window) {
    var catalog = this;
    $scope.restaurant_menu;
    $scope.is_owned;
    $scope.is_rest_owned;
    $scope.all_restaurants;

    catalog.get_all_restaurants = function(){
      $scope.all_restaurants = "";
      $http.get("/restaurants/JSON")
      .then(function(data){
        $scope.all_restaurants = data.data.results;
      });
    }

    catalog.get_menu_by_restaurant = function(restaurant_id){
        $scope.restaurant_menu = "";
    	$http.get("/restaurant/menu/" + restaurant_id)
    	.then(function(data){
    	    $scope.restaurant_menu = data.data.results;
    	});
    };

    catalog.is_item_owned = function(item_id){
        $scope.is_owned = "";
    	$http.get("/restaurant/menu/" + item_id + "/isowned")
    	.then(function(data){
    	    $scope.is_owned = data.data.results[0].answer;
    	});
    };

    catalog.is_rest_owned = function(restaurant_id){
        $scope.is_rest_owned = "";
    	$http.get("/restaurant/" + restaurant_id + "/isowned")
    	.then(function(data){
    	    $scope.is_rest_owned = data.data.results[0].answer;
    	});
    };

    catalog.delete_menu_item = function(restaurant_id, menu_id){
      $window.location.href = "/restaurants/"+restaurant_id+"/"+menu_id+"/delete";
    }

    catalog.edit_menu_item = function(restaurant_id, menu_id){
      $window.location.href = "/restaurants/"+restaurant_id+"/"+menu_id+"/edit";
    }
  });
