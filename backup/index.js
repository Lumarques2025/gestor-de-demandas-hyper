const { Firestore } = require('@google-cloud/firestore');
const fs = require('fs');
const path = require('path');

async function exportarFirestore() {
  const projectId = process.env.FIREBASE_PROJECT_ID;
  const credRaw = process.env.FIREBASE_SERVICE_ACCOUNT;
  // Suporta tanto JSON direto quanto base64
  let credJson;
  try {
    const decoded = Buffer.from(credRaw, 'base64').toString('utf8');
    JSON.parse(decoded);
    credJson = decoded;
  } catch {
    credJson = credRaw;
  }

  if (!projectId || !credJson) {
    console.error('❌ Variáveis FIREBASE_PROJECT_ID e FIREBASE_SERVICE_ACCOUNT são obrigatórias.');
    process.exit(1);
  }

  const credentials = JSON.parse(credJson);
  const db = new Firestore({ projectId, credentials });

  console.log(`🔄 Iniciando backup do projeto: ${projectId}`);

  const backup = {
    geradoEm: new Date().toISOString(),
    projeto: projectId,
    colecoes: {}
  };

  // Listar todas as coleções de nível raiz
  const colecoes = await db.listCollections();
  console.log(`📂 Coleções encontradas: ${colecoes.map(c => c.id).join(', ')}`);

  for (const colRef of colecoes) {
    console.log(`  ↳ Exportando: ${colRef.id}`);
    backup.colecoes[colRef.id] = {};

    const docs = await colRef.get();
    for (const doc of docs.docs) {
      const dadosDoc = { _id: doc.id, ...doc.data() };

      // Exportar subcoleções (ex: workspaces/{id}/data/{key})
      const subcolecoes = await doc.ref.listCollections();
      if (subcolecoes.length > 0) {
        dadosDoc._subcolecoes = {};
        for (const subRef of subcolecoes) {
          const subDocs = await subRef.get();
          dadosDoc._subcolecoes[subRef.id] = subDocs.docs.map(sd => ({
            _id: sd.id,
            ...sd.data()
          }));
        }
      }

      backup.colecoes[colRef.id][doc.id] = dadosDoc;
    }
  }

  const nomeArquivo = `backup-${new Date().toISOString().slice(0, 10)}.json`;
  const caminho = path.join(process.env.OUTPUT_DIR || '.', nomeArquivo);

  fs.writeFileSync(caminho, JSON.stringify(backup, null, 2), 'utf8');

  const tamanhoKB = (fs.statSync(caminho).size / 1024).toFixed(1);
  console.log(`✅ Backup salvo: ${nomeArquivo} (${tamanhoKB} KB)`);
}

exportarFirestore().catch(err => {
  console.error('❌ Erro no backup:', err.message);
  process.exit(1);
});
