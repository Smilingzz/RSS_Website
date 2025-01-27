
let live_rss_data = [];

// Ref in Docs: hXXps://developer[.]mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch


async function get_live_rss_data() {
    const url = "127.0.0.1:8080/get_rss";
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Reponse status: ${response.status}`);
        }
        console.log(response);
    }
    catch {
        console.log("Erroooor");
    }
};

get_live_rss_data();