(async()=>{

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if this cookie string begins with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function compressImage(file, quality = 0.7) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = event => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement("canvas");
                canvas.width = img.width;   // keep original dimensions
                canvas.height = img.height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0);

                canvas.toBlob(blob => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error("Image compression failed"));
                    }
                }, "image/jpeg", quality); // quality between 0.1 and 1.0
            };
            img.src = event.target.result;
        };
        reader.onerror = err => reject(err);
        reader.readAsDataURL(file);
    });
}
  
const title = document.getElementById("title");
const content_tag = document.getElementById("content");
const image_key = document.getElementById("image_key");

const add_image_button = document.getElementById("add_image_button");
const add_image_button_text = document.getElementById("add_image_button_text");
const add_image_modal = document.getElementById("add_image_modal");  
const add_image_modal_select = document.getElementById("add_image_modal_select");
const add_image_modal_close = document.getElementById("add_image_modal_close");
const add_image_modal_input = document.getElementById("add_image_modal_input");

const notes_image_container = document.getElementById("notes_image_container");
const note_image = document.getElementById("note_image");

const write_note_button = document.getElementById("write_note_button");

const loader = document.getElementById("loader");
const loader_title_text = document.getElementById("loader_title_text");
const loader_progress_bar = document.getElementById("loader_progress_bar");
const loader_result_text = document.getElementById("loader_result_text");
const loader_success_button = document.getElementById("loader_success_button");
const loader_error_button = document.getElementById("loader_error_button");
const qr_code_holder = document.getElementById("qr_code_holder");
const qr_code_title = document.getElementById("qr_code_title");
const image_drawer = document.getElementById("image_drawer");
const image_drawer_wrapper = document.getElementById("image_drawer_wrapper");

let has_image = false;
let return_data = null;

write_note_button.addEventListener("click", async()=>{
    if (write_note_button.disabled) return;

    // Check if title and content are not empty
    if (title.value.trim() === "" || content_tag.value.trim() === "") return;

    write_note_button.disabled = true;

    // Avoid duplication of classes
    loader_title_text.classList.remove('--success');
    loader_title_text.classList.remove('--error');
    loader_progress_bar.classList.remove('collapsed');
    loader_success_button.classList.remove('collapsed');
    loader_error_button.classList.remove('collapsed');

    loader.classList.remove("--invisible");
    loader_title_text.textContent = "Uploading Note...";
    loader_result_text.textContent = "Please wait while we upload your notes. It takes a little second!";
    loader_progress_bar.classList.remove('collapsed'); 
    loader_success_button.classList.add('collapsed');
    loader_error_button.classList.add('collapsed');

    let formData = new FormData();
    formData.append("title", title.value);
    formData.append("content", content_tag.value);
    if (has_image){
        formData.append("image_key", image_key.value);
        const file = add_image_modal_input.files[0]; 
        // formData.append("image", add_image_modal_input.files[0]);
        const compressedBlob = await compressImage(file);
        formData.append("image", compressedBlob, file.name);
    }

    const response = await fetch("/api/write/", {
        method: "POST",
        body: formData ,
        headers: {
            "X-CSRFToken": csrftoken
        }
    });

    if (!response.ok){
        loader_title_text.textContent = "Opps! Something went wrong.";
        let message = "There was a problem uploading your note. Please try again.";
        loader_progress_bar.classList.add('collapsed');
        loader_error_button.classList.remove('collapsed');
        try{
            const data = await response.json(); 
            loader_result_text.textContent = data.message || message;
        } catch(e){
            loader_result_text.textContent = message;
        } 
        write_note_button.disabled = false;
        return;
    }

    const data = await response.json();
    loader_progress_bar.classList.add('collapsed');
    loader_title_text.textContent = "Note Uploaded!";
    loader_result_text.textContent =  data?.message || "You can now download the QR code to share your note with your friends.";
    loader_progress_bar.classList.add('collapsed');
    loader_success_button.classList.remove('collapsed'); 
    write_note_button.disabled = false;
    
    return_data = {
        note_id : data?.note_id,
        qr_code_url : data?.qr_code_url,
        title : data?.title
    }

});


loader_success_button.addEventListener("click", function(e){
    const action = e?.target?.getAttribute("data-action");
    if (action === "download" && return_data){ 
        image_drawer.classList.remove("--invisible"); 
        // Generate QR code inside the div
        new QRCode( qr_code_holder, {
            text: return_data?.qr_code_url,
            width: 180,
            height: 180,
        });
        qr_code_title.textContent = return_data?.title || "Maslove Notes";

        domtoimage.toPng(image_drawer_wrapper)
        .then(dataUrl => {
            const link = document.createElement("a");
            link.download = "note.png";
            link.href = dataUrl;
            link.click();
            image_drawer.classList.add("--invisible");
        })
        .catch(err => {
            console.error(err);
            image_drawer.classList.add("--invisible");
        });
 
    } else if (action === "visit" && return_data){
        window.location.href = return_data?.qr_code_url;
    }

});


loader_error_button.addEventListener("click", () => {
    loader.classList.add("--invisible");
});


add_image_modal_input.addEventListener("change", () => {
    note_image.src = URL.createObjectURL(add_image_modal_input.files[0]);
    notes_image_container.style.display = "flex";
    setTimeout(() => {
        notes_image_container.classList.add("expanded");
    }, 100);
    add_image_modal.classList.toggle("--invisible");
    has_image = true;
    add_image_button_text.innerHTML = "Remove Image?"; 
});

add_image_modal_select.addEventListener("click", () => {
    add_image_modal_input.click(); 
});

add_image_modal_close.addEventListener("click", () => {
    add_image_modal.classList.toggle("--invisible");
});

add_image_button.addEventListener("click", () => {  
    if (has_image){
        notes_image_container.classList.remove("expanded");
        has_image = false;
        add_image_button_text.innerHTML = "Add Image?";
        setTimeout(() => {
            notes_image_container.style.display = "none";
            note_image.src = "";
            add_image_modal_input.value = "";
            add_image_modal_input.files = null;
        }, 320);
    } else{
        add_image_modal.classList.toggle("--invisible");
    }
    
});

content_tag.addEventListener("input", () => {
    content_tag.style.height = "auto";
    content_tag.style.height = content_tag.scrollHeight + "px";
});

 


})();