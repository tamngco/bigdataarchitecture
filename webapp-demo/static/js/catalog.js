function getUrlParameter(index) {
  var url = decodeURIComponent(window.location.search.substring(1));
  var parameters = url.split('&');

  for (var iter = 0; iter < parameters.length; iter++) {
    var parameter = parameters[iter].split('=');

    if (parameter[0] === index) {
      return parameter[1] === undefined ? true : parameter[1];
    }
  }
  return '';
};

function retrieveCategory() {
  var category = getUrlParameter('c');
  //if category is not set use a default value
  if ('' == category) {
    category = 0;
  }
  //Update category label
  $('#labelCategory').html(categories[category].name.toUpperCase());
  $('#labelCategory').attr('href', 'products.html?c=' + category);
  return category;
}

function loadProductImages(images) {
  for (var index=0; index < images.length; index++) {
    var html = '<li data-thumb="images/';
    html += images[index];
    html += '">';
    html += '<div class="thumb-image"> <img src="images/';
    html += images[index];
    html += '" data-imagezoom="true" class="img-responsive"> </div>';
    html += '</li>';
    $("#productImages").append(html);
  }
}

function retrieveProduct() {
  var categoryId = retrieveCategory();
  var productId = getUrlParameter('p');
  //if category is not set use a default value
  if ('' == productId) {
    productId = 0;
  }
  var product = products[categoryId][productId];
  if (undefined === product) {
    return;
  }
  $('#labelTitle').html(product.name);
  $('#labelDesc').html(product.description);
  $('#labelDetails').html(product.details);

  /*
  distance: 555.0998000000001,
      dow_created_time: 2,
      hour_created_time: 14,
      suggested_deli_supplier: 1.0,
      destination_address_type: 1.0,
      destination_district: 289.0,
      seller_id: 11017,
      suggested_pickup_supplier: 1.0,
      departure_region: 59.0,
      route: 4.0,
      datetime_created_at: "2023-07-26T14:15:37"
   */

  $('#hidden_distance').val(product.distance);
  $('#hidden_dow_created_time').val(product.dow_created_time);
  $('#hidden_hour_created_time').val(product.hour_created_time);
  $('#suggested_deli_supplier').val(product.suggested_deli_supplier);
  $('#hidden_destination_address_type').val(product.destination_address_type);
  $('#hidden_destination_district').val(product.destination_district);

  var seller_id = product.seller_id;
  var seller_name = product.seller_name;

  var optionValue = seller_id;
  var optionText = seller_name;

  $('#seller_id').append(`<option value="${optionValue}">${optionText}</option>`);

  $('#hidden_suggested_pickup_supplier').val(product.suggested_pickup_supplier);
  $('#hidden_departure_region').val(product.departure_region);
  $('#hidden_route').val(product.route);
  $('#hidden_datetime_created_at').val(product.datetime_created_at);
  loadProductImages(product.images);

  showLastCategory(categoryId);
}

function createItem(name, image, link) {
  var html = '<div class="col-md-4 grid-stn simpleCart_shelfItem">';
  html += '<div class="img">';
  html += '<a href="';
  html += link;
  html += '"><img src="images/';
  html += image;
  html += '" alt="/" class="img-responsive gri-wid"></a>';
  html += '</div>';
  html += '<div class="info">';
  html += '<div class="pull-left styl-hdn">';
  html += '<a href="';
  html += link;
  html += '"><h3>';
  html += name;
  html += '</h3></a>';
  html += '</div>';
  html += '<div class="clearfix"></div>';
  html += '</div>';
  html += '</div>';

  return html;
}

function createCategories(onlyMenu) {
  for (var menuItem=0; menuItem<categories.length; menuItem++) {
    var link = 'products.html?c=' + menuItem;
    //Append categories to the main menu in the header
    var menuText = '<li><a href="';
    menuText += link;
    menuText += '">';
    menuText += categories[menuItem].name;
    menuText += '</a></li>';
    $("#menu").append(menuText);

    if (true !== onlyMenu) {
      //Apend category name and image to the list-style
      $("#categoriesList").append(createItem(
        categories[menuItem].name, categories[menuItem].image, link));
    }
  }

  $("#categoriesList").append('<div class="clearfix"></div>');
}

function createProducts(category) {
  var selectedProducts = products[category];
  if (undefined === selectedProducts) {
    return;
  }
  for (var iter=0; iter<selectedProducts.length; iter++) {
    var link = 'single.html?c=' + category + '&p=' + iter;
    //Apend category name and image to the list-style
    $("#productsList").append(createItem(
      selectedProducts[iter].name, selectedProducts[iter].thumbnail, link));
  }

  $("#productsList").append('<div class="clearfix"></div>');
}

function showLastCategory(currentCategory) {
  var lastCategory = products.length - 1;
  // Check and do a typecast to integer if needed
  if (false === Number.isInteger(currentCategory)) {
    currentCategory = parseInt(currentCategory);
  }
  if ( (currentCategory === lastCategory) ||
       (-1 === categoriesShowAdditionalList.indexOf(currentCategory)) ) {
    return;
  }
  createProducts(lastCategory);
}
