function add_answer() {
    var p = d.createElement('p'),
        cloneField = field.cloneNode(),
        cloneButton = but.cloneNode();
    p.id = 'new_answer_'+id;
    cloneField.name = 'new_answer';
    cloneField.value = '';
    cloneButton.name ='new_answer_'+id;
    id+=1;
    p.appendChild(cloneField);
    p.appendChild(cloneButton);
    newFields.appendChild(p);
}

function delete_answer(id_p) {
    let p = d.getElementById(id_p)
    p.remove();
}


var d = document,
    myForm = d.getElementById('form'),
    newFields = myForm.querySelector('#new_fields'),
    field = myForm.querySelector('input[name=answer]'),
    but = myForm.querySelector('input[id=delete]'),
    butAdd = d.getElementById('add_answer'),
    id=1;
butAdd.addEventListener('click', add_answer, false);
