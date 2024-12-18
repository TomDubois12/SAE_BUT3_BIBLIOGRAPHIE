export async function loadCSVName() {
    const response = await fetch('./json/userSettings.json');
    if (!response.ok) {
        throw new Error(`Erreur de chargement du fichier JSON : ${response.statusText}`);
    }
    const data = await response.json();
    return data.CSVChoose;
}

export async function countTotalLines(csvPath) {
    const response = await fetch(csvPath);
    if (!response.ok) throw new Error(`Impossible de charger le fichier CSV : ${response.statusText}`);
    const text = await response.text();
    return text.split("\n").filter(line => line.trim() !== "").length - 1; // Exclut l'en-tête
}

export async function updateProgressBar(jsonPath, totalLines) {
    try {
        const response = await fetch(jsonPath);
        if (!response.ok) throw new Error(`Erreur de chargement du fichier JSON : ${response.statusText}`);
        
        const jsonData = await response.json();
        const currentInserts = Object.keys(jsonData).length;

        // Mise à jour de la barre
        const progressPercent = Math.min((currentInserts / totalLines) * 100, 100);
        document.getElementById("progress-bar").style.width = `${progressPercent}%`;
        document.getElementById("progress-bar").textContent = `${Math.round(progressPercent)}%`;

        // Mise à jour de l'estimation
        const timePerInsert = 15 / 10; // Exemple de temps par insert
        const estimatedTimeLeft = ((totalLines - currentInserts) * timePerInsert) / 60;
        const minutes = Math.floor(estimatedTimeLeft);
        const seconds = Math.round((estimatedTimeLeft - minutes) * 60);

        document.getElementById("estimated-time").textContent = 
            `Estimation du temps restant : ${minutes} minutes et ${seconds} secondes`;
    } catch (error) {
        console.error(error);
        document.getElementById("estimated-time").textContent = "Création du fichier de stockage...";
    }
}

export async function main() {
    const CSVChoose = await loadCSVName();
    const csvPath = `../Data/${CSVChoose}`;
    const totalLines = await countTotalLines(csvPath);

    const jsonPath = '../cache_doi.json';
    setInterval(() => updateProgressBar(jsonPath, totalLines), 1000);
}
