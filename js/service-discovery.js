function isJSONString(str) {
    try {
        JSON.parse(str);
        return true;
    } catch (e) {
        return false;
    }
}


function buildNavbarContent(data) {
    var jsonData = ""
    if (isJSONString(data)) {
        jsonData = JSON.parse(data);
    } else {
        console.log('La chaîne n\'est pas un JSON valide.');
    }

    // Création des onglets 
    var isFirstTab = true; // Variable pour suivre le premier onglet
    var isSelected = 'true';
    var htmlContent = '';
    // Parcourez chaque clé dans les données JSON
    for (var key in jsonData) {
        // Détermine la valeur de aria-selected en fonction de isFirstTab
        isSelected = isFirstTab ? 'active fw-bold' : '';
        console.log('Building nav bar content. isFirstTab is ' + isFirstTab + ' and isSelected is ' + isSelected);
        htmlContent += '<div id="' + key + '" class="btn text-capitalize nav-link ' + isSelected + '">' + key + '</div>';
        // Après le premier passage,isFirstTab est false
        isFirstTab = false;
    }
    console.log('HTML content is ' + htmlContent);
    
    // Retourner le contenu HTML généré
    return htmlContent;
}


// Fonction pour traiter les données JSON et générer le contenu HTML
function processJSONData(data) {
    var jsonData = ""
    if (isJSONString(data)) {
        jsonData = JSON.parse(data);
    } else {
        console.log('La chaîne n\'est pas un JSON valide.');
    }

    // Création des panes 
    var isFirstPane = true; // Variable pour suivre le premier pane
    var isSelected = 'active show';
    var htmlContent = '';
    htmlContent += '<div class="tab-content" id="v-pills-tabContent">';
    for (var key in jsonData) {       
        // Détermine la valeur de aria-selected en fonction de isFirstTab
        isSelected = isFirstPane ? 'active show' : '';
        console.log('Building panes. isFirstPane is ' + isFirstPane + ' and isSelected is ' + isSelected);
        htmlContent += '<div class="tab-pane fade ' + isSelected + '" id="pane-' + key + '" role="tabpanel" aria-labelledby="v-pills-' + key + '-tab">';
        if (Array.isArray(jsonData[key])) {
            // Si la valeur est un tableau
            htmlContent += processArray(key, jsonData[key]);
        } else if (typeof jsonData[key] === 'object') {
            // Si la valeur est un objet
            htmlContent += processObject(key, jsonData[key]);
        } else {
            // Si la valeur est une chaîne ou une autre primitive
            htmlContent += processPrimitive(key, jsonData[key]);
        }
        htmlContent += '</div>';

        // Après le premier passage, isFirstTab est false
        isFirstPane = false;
    }
    htmlContent += '</div>';
    // Retourne le contenu HTML généré
    return htmlContent;
}

// Fonction pour traiter un tableau
function processArray(key, array, inCard = true) {
    var htmlContent = '';

    // Parcourez chaque élément du tableau
    array.forEach(function (item) {
        if (typeof item === 'object') {
            // Si l'élément est un objet, le traitez comme un objet
            htmlContent += processObject(key, item);
        } else {
            // Sinon, le traite comme une valeur primitive
            htmlContent += '<ul><li>' + item + '</li></ul>';
        }
    });

    return htmlContent;
}

// Fonction pour traiter un objet
function processObject(key, obj) {
    var htmlContent = '';
    var updatedOn;

    htmlContent += '<ul>';

    // Parcourez les propriétés de l'objet
    for (var prop in obj) {
        if (typeof obj[prop] === 'object') {
            // Si la propriété est un objet, traite l'objet en appelant récursivement processObject
            htmlContent += '<li>' + prop + ':</li>';
            htmlContent += processObject(key, obj[prop]);
        } else if (Array.isArray(obj[prop])) {
            // Si la propriété est un tableau, traite les éléments du tableau
            htmlContent += '<li>' + prop + ':</li>';
            htmlContent += processArray(key, obj[prop], false);
        } else if (prop !== 'Updated on') {
            htmlContent += '<li>';
            htmlContent += '<span class="font-weight-bold">' + prop + '</span>: ' + obj[prop] + '<br>';
            htmlContent += '</li>';
        } else {
            updatedOn = obj['Updated on'];
        }
    }

    htmlContent += '</ul>';

    return htmlContent;
}

// Fonction pour traiter une valeur primitive
function processPrimitive(key, value) {
    var htmlContent = '';
    htmlContent += '<ul><li>' + value + '</li></ul>';
    return htmlContent;
}
