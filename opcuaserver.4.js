const opcua = require("node-opcua");


const logger = console;

// Function to calculate check digit for GS1 serial numbers
function calculateCheckDigit(gs1Prefix, serialNumber) {
  const gs1Data = gs1Prefix + serialNumber;
  let total = 0;

  for (let i = 0; i < gs1Data.length; i++) {
    const digit = parseInt(gs1Data.charAt(i));
    const weight = i % 2 === 0 ? 3 : 1;
    total += digit * weight;
  }

  const checkDigit = (10 - (total % 10)) % 10;

  return checkDigit;
}

// Function to slice a list into equally sized pieces
function chopSerialList(serials, pieceSize) {
  const slicedSerials = [];
  for (let i = 0; i < serials.length; i += pieceSize) {
    const slice = serials.slice(i, i + pieceSize);
    slicedSerials.push(slice);
  }
  return slicedSerials;
}

// Function to generate GS1 serial numbers for each cell
function generateSerialList(gs1Prefix, numSerials) {
  const gs1Serials = [];

  for (let serial = 0; serial < numSerials; serial++) {
    const serialNumber = serial.toString().padStart(9, '0');
    const checkDigit = calculateCheckDigit(gs1Prefix, serialNumber);
    const gs1Serial = parseInt(gs1Prefix + serialNumber + checkDigit);
    gs1Serials.push(gs1Serial);
  }

  return gs1Serials;
}

// Function to generate simulated data for each tag
function generateSimulatedData(serialNumber = 0) {
  return {
    SN: serialNumber,
    Temperature: random.uniform(20, 30),
    Pressure: random.uniform(1000, 1050),
    Torque: random.uniform(5, 30),
    Humidity: random.uniform(40, 60),
    Light: random.uniform(500, 1000),
    Voltage: random.uniform(110, 240),
    Watts: random.uniform(50, 500),
  };
}

// Function to create an equipment node under the parent_node with the given equipment_name
// and add tags for the equipment using the namespace_idx
async function createEquipmentNode(parentNode, equipmentName, namespaceIdx) {
  const equipmentNode = await parentNode.addObject({
    organizedBy: namespaceIdx,
    browseName: equipmentName,
  });

  const tags = {};

  const simulatedData = generateSimulatedData();
  for (const tagName of Object.keys(simulatedData)) {
    let tagValue = 0.0;
    if (tagName === 'SN') {
      tagValue = 0;
    }

    tags[tagName] = await equipmentNode.addVariable({
      componentOf: equipmentNode,
      nodeId: `s=${tagName}`,
      dataType: 'Double',
      value: { dataType: 'Double', value: tagValue },
    });
  }

  return tags;
}

// Function to update tags for each equipment
async function updateTagsForEquipment(equipmentName, tags, serialNumber) {
  const timeDelay = Math.abs(random.gauss(3, 0.25)) * 1000;
  await new Promise((resolve) => setTimeout(resolve, timeDelay));

  const data = generateSimulatedData(serialNumber);
  for (const [tagName, value] of Object.entries(data)) {
    await tags[tagName].writeValue(value);
  }

  if (data.SN !== 0) {
    logger.info(`Cell created with SN ${data.SN} for Equipment ${equipmentName}`);
  } else {
    logger.error(`Faulty cell created for Equipment ${equipmentName}`);
  }
}

async function main() {
  const server = new opcua.OPCUAServer();

  await server.initialize();

  server.endpoints.push({ endpointUrl: 'opc.tcp://0.0.0.0:4840/freeopcua/server/' });
  server.serverInfo.applicationName.text = 'Battery Manufacturing Server';

  server.securityPolicies = [
    opcua.SecurityPolicy.None,
    opcua.SecurityPolicy.Basic256Sha256,
    opcua.SecurityPolicy.Basic256Sha256,
  ];

  const addressSpace = await server.getOwnNamespace();

  const simulatedDataNode = addressSpace.addObject({
    organizedBy: addressSpace.rootFolder.objects,
    browseName: 'SimulatedData',
  });

  const numEquipments = 4;
  const equipments = {};

  for (let i = 0; i < numEquipments; i++) {
    const equipmentName = `Equipment_${i + 1}`;
    equipments[equipmentName] = await createEquipmentNode(
      simulatedDataNode,
      equipmentName,
      addressSpace.namespaceIndex
    );
  }

  logger.info('Create S/N batch');
  const bufferSerials = generateSerialList('123', 1000000);

  await server.start();

  while (true) {
    const tasks = [];

    for (const [equipmentName, tags] of Object.entries(equipments)) {
      const randomNum = Math.random();
      const condition = randomNum > 0.05;
      let serialNumber;

      if (condition) {
        serialNumber = bufferSerials.shift();
      } else {
        serialNumber = 0;
      }

      const task = updateTagsForEquipment(equipmentName, tags, serialNumber);
      tasks.push(task);
    }

    await Promise.all(tasks);
  }
}

main();
