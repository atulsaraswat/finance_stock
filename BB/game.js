import * as THREE from "three";

// ── Config (Hard Mode) ──────────────────────────────────────────────
const ARENA_SIZE = 40;
const WALL_HEIGHT = 6;
const PLAYER_SPEED = 0.16;
const TURN_SPEED = 0.042;
const BULLET_SPEED = 1.15;
const PLAYER_BULLET_DAMAGE = 16;
const ENEMY_BULLET_DAMAGE = 24;
const FIRE_COOLDOWN = 420;
const MAG_SIZE = 10;
const RESERVE_AMMO = 40;
const RELOAD_TIME = 2000;
const MAX_HP = 80;
const ENEMY_MAX_HP = 130;
const BOT_SPEED = 0.15;
const BOT_TURN_SPEED = 0.05;
const BOT_FIRE_RANGE = 30;
const BOT_FIRE_COOLDOWN = 480;
const BOT_BURST_SIZE = 3;
const BOT_BURST_GAP = 120;
const BOT_ACCURACY = 0.91;
const ENEMY_BULLET_SPEED = 1.5;

// ── State ───────────────────────────────────────────────────────────
const keys = {};
let gameRunning = false;
let playerHP = MAX_HP;
let enemyHP = ENEMY_MAX_HP;
let kills = 0;
let lastPlayerShot = 0;
let lastBotShot = 0;
let playerYaw = 0;
let botYaw = Math.PI;
let magAmmo = MAG_SIZE;
let reserveAmmo = RESERVE_AMMO;
let isReloading = false;
let reloadStart = 0;
let gameStartTime = 0;
let botBurstCount = 0;
let botStrafeDir = 1;
let lastBotStrafeSwitch = 0;
let damageVignetteTimeout = 0;
let hitMarkerTimeout = 0;
let hudMessageTimeout = 0;
let prevPlayerX = 0;
let prevPlayerZ = 0;

const bullets = [];
const particles = [];

// ── DOM ─────────────────────────────────────────────────────────────
const startScreen = document.getElementById("start-screen");
const gameOverScreen = document.getElementById("game-over");
const startBtn = document.getElementById("start-btn");
const restartBtn = document.getElementById("restart-btn");
const playerHealthBar = document.getElementById("player-health");
const enemyHealthBar = document.getElementById("enemy-health");
const playerHpText = document.getElementById("player-hp-text");
const enemyHpText = document.getElementById("enemy-hp-text");
const killsEl = document.getElementById("kills");
const ammoFlash = document.getElementById("ammo-flash");
const resultTitle = document.getElementById("result-title");
const resultMessage = document.getElementById("result-message");
const missionTimer = document.getElementById("mission-timer");
const threatLevel = document.getElementById("threat-level");
const ammoCurrent = document.getElementById("ammo-current");
const ammoReserve = document.getElementById("ammo-reserve");
const reloadBarWrap = document.getElementById("reload-bar-wrap");
const reloadBar = document.getElementById("reload-bar");
const weaponStatus = document.getElementById("weapon-status");
const enemyDistance = document.getElementById("enemy-distance");
const crosshair = document.getElementById("crosshair");
const hitMarker = document.getElementById("hit-marker");
const damageVignette = document.getElementById("damage-vignette");
const hudMessage = document.getElementById("hud-message");
const enemyPointer = document.getElementById("enemy-pointer");
const enemyPointerArrow = document.getElementById("enemy-pointer-arrow");
const enemyPointerDist = document.getElementById("enemy-pointer-dist");
const minimapCanvas = document.getElementById("minimap");
const minimapCtx = minimapCanvas.getContext("2d");

// ── Three.js setup ──────────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a14);
scene.fog = new THREE.Fog(0x0a0a14, 20, 55);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 1.7, 12);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Lighting
const ambient = new THREE.AmbientLight(0x334466, 0.6);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffeedd, 1.1);
sun.position.set(15, 25, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1;
sun.shadow.camera.far = 60;
sun.shadow.camera.left = -25;
sun.shadow.camera.right = 25;
sun.shadow.camera.top = 25;
sun.shadow.camera.bottom = -25;
scene.add(sun);

const rimLight = new THREE.PointLight(0x4488ff, 0.8, 50);
rimLight.position.set(-10, 8, -10);
scene.add(rimLight);

const rimLight2 = new THREE.PointLight(0xff4444, 0.6, 50);
rimLight2.position.set(10, 8, 10);
scene.add(rimLight2);

// ── Arena geometry ──────────────────────────────────────────────────
function createArena() {
  const half = ARENA_SIZE / 2;

  // Floor
  const floorGeo = new THREE.PlaneGeometry(ARENA_SIZE, ARENA_SIZE, 20, 20);
  const floorMat = new THREE.MeshStandardMaterial({
    color: 0x1a1a28,
    roughness: 0.85,
    metalness: 0.15,
  });
  const floor = new THREE.Mesh(floorGeo, floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  // Grid lines on floor
  const gridHelper = new THREE.GridHelper(ARENA_SIZE, 20, 0x334466, 0x222233);
  gridHelper.position.y = 0.01;
  scene.add(gridHelper);

  // Walls
  const wallMat = new THREE.MeshStandardMaterial({
    color: 0x2a2a3a,
    roughness: 0.7,
    metalness: 0.3,
  });

  const wallGeo = new THREE.BoxGeometry(ARENA_SIZE, WALL_HEIGHT, 0.8);
  const walls = [
    { pos: [0, WALL_HEIGHT / 2, -half], rot: 0 },
    { pos: [0, WALL_HEIGHT / 2, half], rot: 0 },
    { pos: [-half, WALL_HEIGHT / 2, 0], rot: Math.PI / 2 },
    { pos: [half, WALL_HEIGHT / 2, 0], rot: Math.PI / 2 },
  ];

  walls.forEach(({ pos, rot }) => {
    const wall = new THREE.Mesh(wallGeo, wallMat);
    wall.position.set(...pos);
    wall.rotation.y = rot;
    wall.castShadow = true;
    wall.receiveShadow = true;
    scene.add(wall);
  });

  // Cover pillars
  const pillarMat = new THREE.MeshStandardMaterial({ color: 0x3a3a50, roughness: 0.6, metalness: 0.4 });
  const pillarPositions = [
    [-8, 0, -8], [8, 0, -8], [-8, 0, 8], [8, 0, 8],
    [0, 0, 0], [-12, 0, 0], [12, 0, 0], [0, 0, -12], [0, 0, 12],
  ];

  pillarPositions.forEach(([x, , z]) => {
    const pillar = new THREE.Mesh(new THREE.BoxGeometry(2.5, 3.5, 2.5), pillarMat);
    pillar.position.set(x, 1.75, z);
    pillar.castShadow = true;
    pillar.receiveShadow = true;
    scene.add(pillar);
  });

  // Neon trim on walls
  const trimMat = new THREE.MeshBasicMaterial({ color: 0x00aaff });
  walls.forEach(({ pos, rot }) => {
    const trim = new THREE.Mesh(new THREE.BoxGeometry(ARENA_SIZE, 0.15, 0.2), trimMat);
    trim.position.set(pos[0], 0.3, pos[2]);
    trim.rotation.y = rot;
    scene.add(trim);
  });
}

createArena();

// ── Enemy bot mesh ──────────────────────────────────────────────────
const enemyGlowParts = [];

function addShadow(mesh) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function createEnemyBot() {
  const group = new THREE.Group();

  const armorDark = new THREE.MeshStandardMaterial({ color: 0x1c1c26, roughness: 0.55, metalness: 0.75 });
  const armorRed = new THREE.MeshStandardMaterial({ color: 0x6b1515, roughness: 0.45, metalness: 0.6 });
  const armorPlate = new THREE.MeshStandardMaterial({ color: 0x2a2a38, roughness: 0.4, metalness: 0.85 });
  const rubber = new THREE.MeshStandardMaterial({ color: 0x111118, roughness: 0.95, metalness: 0.05 });
  const glowRed = new THREE.MeshBasicMaterial({ color: 0xff2200 });
  const glowDim = new THREE.MeshBasicMaterial({ color: 0x881100 });

  // Legs & boots
  [-0.22, 0.22].forEach((x) => {
    const leg = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.75, 0.24), rubber));
    leg.position.set(x, 0.45, 0);
    group.add(leg);

    const boot = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.18, 0.38), armorPlate));
    boot.position.set(x, 0.09, 0.06);
    group.add(boot);

    const kneePad = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.14, 0.16), armorRed));
    kneePad.position.set(x, 0.62, 0.1);
    group.add(kneePad);
  });

  // Waist & belt
  const waist = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.72, 0.28, 0.42), armorDark));
  waist.position.y = 0.98;
  group.add(waist);

  const belt = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.76, 0.1, 0.44), armorPlate));
  belt.position.y = 0.86;
  group.add(belt);

  // Torso
  const torso = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.82, 0.72, 0.48), armorDark));
  torso.position.y = 1.48;
  group.add(torso);

  const chestPlate = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.58, 0.12), armorRed));
  chestPlate.position.set(0, 1.5, 0.22);
  group.add(chestPlate);

  // Enemy insignia (red X on chest)
  const markH = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.06, 0.04), glowRed));
  markH.position.set(0, 1.5, 0.29);
  markH.rotation.z = Math.PI / 4;
  group.add(markH);
  const markH2 = markH.clone();
  markH2.rotation.z = -Math.PI / 4;
  group.add(markH2);
  enemyGlowParts.push(markH.material, markH2.material);

  // Shoulder pads
  [-0.52, 0.52].forEach((x) => {
    const pad = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.18, 0.32), armorPlate));
    pad.position.set(x, 1.78, 0);
    pad.rotation.z = x > 0 ? -0.25 : 0.25;
    group.add(pad);

    const spike = addShadow(new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.18, 4), armorRed));
    spike.position.set(x, 1.92, 0);
    spike.rotation.x = Math.PI;
    group.add(spike);
  });

  // Arms
  [-0.58, 0.58].forEach((x, i) => {
    const upperArm = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.42, 0.2), armorDark));
    upperArm.position.set(x, 1.38, 0);
    group.add(upperArm);

    const forearm = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.38, 0.18), armorPlate));
    forearm.position.set(x, 0.98, i === 1 ? 0.12 : 0);
    group.add(forearm);
  });

  // Rifle (held in right hand)
  const rifle = new THREE.Group();
  const stock = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.14, 0.28), rubber));
  stock.position.set(0, 0, -0.18);
  rifle.add(stock);

  const receiver = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.16, 0.42), armorPlate));
  rifle.add(receiver);

  const barrel = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.55, 8), armorPlate));
  barrel.rotation.x = Math.PI / 2;
  barrel.position.set(0, 0.02, 0.42);
  rifle.add(barrel);

  const scope = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.18, 8), armorDark));
  scope.rotation.x = Math.PI / 2;
  scope.position.set(0, 0.12, 0.08);
  rifle.add(scope);

  const muzzleFlashPad = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 0.04), glowDim);
  muzzleFlashPad.position.set(0, 0.02, 0.7);
  rifle.add(muzzleFlashPad);
  enemyGlowParts.push(muzzleFlashPad.material);

  rifle.position.set(0.52, 1.12, 0.38);
  rifle.rotation.y = 0.08;
  group.add(rifle);

  // Helmet
  const neckGuard = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.26, 0.14, 8), armorPlate));
  neckGuard.position.y = 1.92;
  group.add(neckGuard);

  const helmet = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.58, 0.38, 0.52), armorDark));
  helmet.position.y = 2.18;
  group.add(helmet);

  const helmetTop = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.12, 0.42), armorPlate));
  helmetTop.position.y = 2.42;
  group.add(helmetTop);

  const visorFrame = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.52, 0.16, 0.08), armorRed));
  visorFrame.position.set(0, 2.14, 0.24);
  group.add(visorFrame);

  // Glowing red eyes
  [-0.12, 0.12].forEach((x) => {
    const eye = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.06, 0.04), glowRed.clone());
    eye.position.set(x, 2.14, 0.29);
    group.add(eye);
    enemyGlowParts.push(eye.material);
  });

  const brow = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.54, 0.06, 0.1), armorPlate));
  brow.position.set(0, 2.26, 0.22);
  group.add(brow);

  // Back antenna & power pack
  const backpack = addShadow(new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.48, 0.22), armorDark));
  backpack.position.set(0, 1.48, -0.28);
  group.add(backpack);

  const antenna = addShadow(new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.55, 6), armorPlate));
  antenna.position.set(0.12, 2.05, -0.32);
  group.add(antenna);

  const statusLight = new THREE.Mesh(new THREE.SphereGeometry(0.05, 8, 8), glowRed.clone());
  statusLight.position.set(-0.1, 1.72, -0.38);
  group.add(statusLight);
  enemyGlowParts.push(statusLight.material);

  // Menacing red under-glow
  const enemyLight = new THREE.PointLight(0xff2200, 0.35, 4);
  enemyLight.position.set(0, 1.2, 0.4);
  group.add(enemyLight);

  return group;
}

const botGroup = createEnemyBot();
botGroup.position.set(0, 0, -12);
scene.add(botGroup);

// Weapon model (visible at bottom of screen)
const weaponGroup = new THREE.Group();
const gunBody = new THREE.Mesh(
  new THREE.BoxGeometry(0.12, 0.12, 0.7),
  new THREE.MeshStandardMaterial({ color: 0x445566, metalness: 0.9, roughness: 0.2 })
);
gunBody.position.set(0.25, -0.15, -0.5);
weaponGroup.add(gunBody);

const gunBarrel = new THREE.Mesh(
  new THREE.CylinderGeometry(0.04, 0.04, 0.3, 8),
  new THREE.MeshStandardMaterial({ color: 0x222233, metalness: 1, roughness: 0.1 })
);
gunBarrel.rotation.x = Math.PI / 2;
gunBarrel.position.set(0.25, -0.12, -0.85);
weaponGroup.add(gunBarrel);

camera.add(weaponGroup);
scene.add(camera);

// ── Collision helpers ─────────────────────────────────────────────
const pillars = [
  [-8, -8], [8, -8], [-8, 8], [8, 8],
  [0, 0], [-12, 0], [12, 0], [0, -12], [0, 12],
].map(([x, z]) => ({ x, z, r: 1.8 }));

function clampToArena(x, z) {
  const margin = 1.2;
  const half = ARENA_SIZE / 2 - margin;
  return [
    Math.max(-half, Math.min(half, x)),
    Math.max(-half, Math.min(half, z)),
  ];
}

function resolvePillarCollision(x, z, radius = 0.5) {
  let nx = x;
  let nz = z;
  for (const p of pillars) {
    const dx = nx - p.x;
    const dz = nz - p.z;
    const dist = Math.sqrt(dx * dx + dz * dz);
    const minDist = p.r + radius;
    if (dist < minDist && dist > 0.001) {
      const push = (minDist - dist) / dist;
      nx += dx * push;
      nz += dz * push;
    }
  }
  return clampToArena(nx, nz);
}

// ── Bullets & effects ───────────────────────────────────────────────
function spawnBullet(origin, direction, isPlayer, speed = BULLET_SPEED) {
  const geo = new THREE.SphereGeometry(isPlayer ? 0.08 : 0.07, 8, 8);
  const mat = new THREE.MeshBasicMaterial({
    color: isPlayer ? 0xffcc44 : 0xff4444,
  });
  const mesh = new THREE.Mesh(geo, mat);

  const dir = direction.clone().normalize();
  mesh.position.copy(origin);
  scene.add(mesh);

  bullets.push({
    mesh,
    velocity: dir.multiplyScalar(speed),
    isPlayer,
    life: 120,
  });
}

function spawnImpact(pos, color = 0xffaa44) {
  for (let i = 0; i < 8; i++) {
    const geo = new THREE.SphereGeometry(0.06, 4, 4);
    const mat = new THREE.MeshBasicMaterial({ color });
    const p = new THREE.Mesh(geo, mat);
    p.position.copy(pos);
    scene.add(p);

    const angle = Math.random() * Math.PI * 2;
    const speed = 0.05 + Math.random() * 0.1;
    particles.push({
      mesh: p,
      velocity: new THREE.Vector3(
        Math.cos(angle) * speed,
        Math.random() * 0.08,
        Math.sin(angle) * speed
      ),
      life: 20 + Math.random() * 15,
    });
  }
}

function flashMuzzle() {
  ammoFlash.classList.add("active");
  setTimeout(() => ammoFlash.classList.remove("active"), 60);

  weaponGroup.position.z = 0.08;
  setTimeout(() => { weaponGroup.position.z = 0; }, 80);
}

function showHudMessage(text, duration = 2000) {
  hudMessage.textContent = text;
  hudMessage.classList.add("show");
  clearTimeout(hudMessageTimeout);
  hudMessageTimeout = setTimeout(() => hudMessage.classList.remove("show"), duration);
}

function showHitMarker() {
  hitMarker.classList.add("show");
  clearTimeout(hitMarkerTimeout);
  hitMarkerTimeout = setTimeout(() => hitMarker.classList.remove("show"), 120);
}

function flashDamage() {
  damageVignette.classList.add("active");
  clearTimeout(damageVignetteTimeout);
  damageVignetteTimeout = setTimeout(() => damageVignette.classList.remove("active"), 250);
}

function startReload() {
  if (isReloading || magAmmo >= MAG_SIZE || reserveAmmo <= 0) return;
  isReloading = true;
  reloadStart = performance.now();
  reloadBarWrap.classList.remove("hidden");
  weaponStatus.textContent = "RELOADING";
  weaponStatus.className = "weapon-status reloading";
  showHudMessage("RELOADING...");
}

function finishReload() {
  const needed = MAG_SIZE - magAmmo;
  const loaded = Math.min(needed, reserveAmmo);
  magAmmo += loaded;
  reserveAmmo -= loaded;
  isReloading = false;
  reloadBarWrap.classList.add("hidden");
  reloadBar.style.width = "0%";
  weaponStatus.textContent = magAmmo === 0 ? "EMPTY" : "READY";
  weaponStatus.className = magAmmo === 0 ? "weapon-status empty" : "weapon-status";
}

function updateReload(now) {
  if (!isReloading) return;
  const progress = Math.min(1, (now - reloadStart) / RELOAD_TIME);
  reloadBar.style.width = `${progress * 100}%`;
  if (progress >= 1) finishReload();
}

// ── Shooting ────────────────────────────────────────────────────────
function playerShoot() {
  const now = performance.now();
  if (isReloading) return;

  if (magAmmo <= 0) {
    weaponStatus.textContent = "EMPTY";
    weaponStatus.className = "weapon-status empty";
    if (reserveAmmo > 0) startReload();
    return;
  }

  if (now - lastPlayerShot < FIRE_COOLDOWN) return;
  lastPlayerShot = now;
  magAmmo--;

  const origin = camera.position.clone();
  const direction = new THREE.Vector3(0, 0, -1);
  direction.applyQuaternion(camera.quaternion);

  spawnBullet(origin, direction, true);
  flashMuzzle();

  if (magAmmo === 0 && reserveAmmo > 0) {
    startReload();
  }
}

function botShoot() {
  const now = performance.now();
  if (now - lastBotShot < BOT_FIRE_COOLDOWN) return;
  if (botBurstCount >= BOT_BURST_SIZE && now - lastBotShot < BOT_BURST_GAP) return;

  const toPlayer = new THREE.Vector3(
    camera.position.x - botGroup.position.x,
    0,
    camera.position.z - botGroup.position.z
  );
  const dist = toPlayer.length();
  if (dist > BOT_FIRE_RANGE) return;

  lastBotShot = now;
  botBurstCount = (botBurstCount + 1) % (BOT_BURST_SIZE + 1);

  // Lead target based on player movement
  const playerVelX = camera.position.x - prevPlayerX;
  const playerVelZ = camera.position.z - prevPlayerZ;
  const leadTime = dist / ENEMY_BULLET_SPEED;
  const predictedX = camera.position.x + playerVelX * leadTime * 8;
  const predictedZ = camera.position.z + playerVelZ * leadTime * 8;

  const direction = new THREE.Vector3(
    predictedX - botGroup.position.x,
    0,
    predictedZ - botGroup.position.z
  ).normalize();
  direction.y = (camera.position.y - 1.5) / dist;

  if (Math.random() > BOT_ACCURACY) {
    direction.x += (Math.random() - 0.5) * 0.18;
    direction.z += (Math.random() - 0.5) * 0.18;
    direction.y += (Math.random() - 0.5) * 0.1;
  }

  const origin = new THREE.Vector3(
    botGroup.position.x + direction.x * 0.5,
    1.5,
    botGroup.position.z + direction.z * 0.5
  );

  spawnBullet(origin, direction, false, ENEMY_BULLET_SPEED);
}

// ── Damage & UI ─────────────────────────────────────────────────────
function updateHealthUI() {
  playerHealthBar.style.width = `${Math.max(0, playerHP)}%`;
  enemyHealthBar.style.width = `${Math.max(0, enemyHP)}%`;
  playerHpText.textContent = Math.max(0, playerHP);
  enemyHpText.textContent = Math.max(0, enemyHP);
}

function takeDamage(isPlayer, amount) {
  if (isPlayer) {
    playerHP = Math.max(0, playerHP - amount);
  } else {
    enemyHP = Math.max(0, enemyHP - amount);
  }
  updateHealthUI();

  if (playerHP <= 0 || enemyHP <= 0) {
    endGame(enemyHP <= 0);
  }
}

function endGame(victory) {
  gameRunning = false;
  gameOverScreen.classList.remove("hidden", "victory", "defeat");
  gameOverScreen.classList.add(victory ? "victory" : "defeat");
  resultTitle.textContent = victory ? "Victory!" : "Defeated";
  resultMessage.textContent = victory
    ? "You eliminated the arena bot."
    : "The bot got the better of you. Try again!";
  if (victory) {
    kills++;
    killsEl.textContent = kills;
  }
}

function resetGame() {
  playerHP = MAX_HP;
  enemyHP = MAX_HP;
  playerYaw = 0;
  botYaw = Math.PI;
  lastPlayerShot = 0;
  lastBotShot = 0;

  camera.position.set(0, 1.7, 12);
  camera.rotation.set(0, 0, 0);
  camera.rotation.order = "YXZ";

  botGroup.position.set(0, 0, -12);
  botGroup.rotation.y = 0;

  bullets.forEach((b) => scene.remove(b.mesh));
  bullets.length = 0;
  particles.forEach((p) => scene.remove(p.mesh));
  particles.length = 0;

  updateHealthUI();
  gameOverScreen.classList.add("hidden");
  gameRunning = true;
}

// ── Bot AI ──────────────────────────────────────────────────────────
function updateBot() {
  const dx = camera.position.x - botGroup.position.x;
  const dz = camera.position.z - botGroup.position.z;
  const dist = Math.sqrt(dx * dx + dz * dz);

  const targetAngle = Math.atan2(dx, dz);
  let angleDiff = targetAngle - botYaw;
  while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
  while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;

  botYaw += Math.sign(angleDiff) * Math.min(Math.abs(angleDiff), BOT_TURN_SPEED);
  botGroup.rotation.y = botYaw + Math.PI;

  const idealDist = 10;
  if (dist > idealDist + 2) {
    const moveX = Math.sin(botYaw) * BOT_SPEED;
    const moveZ = Math.cos(botYaw) * BOT_SPEED;
    const [nx, nz] = resolvePillarCollision(
      botGroup.position.x + moveX,
      botGroup.position.z + moveZ,
      0.5
    );
    botGroup.position.x = nx;
    botGroup.position.z = nz;
  } else if (dist < idealDist - 3) {
    const moveX = -Math.sin(botYaw) * BOT_SPEED * 0.7;
    const moveZ = -Math.cos(botYaw) * BOT_SPEED * 0.7;
    const [nx, nz] = resolvePillarCollision(
      botGroup.position.x + moveX,
      botGroup.position.z + moveZ,
      0.5
    );
    botGroup.position.x = nx;
    botGroup.position.z = nz;
  } else {
    // Strafe
    const strafe = Math.sin(performance.now() * 0.001) * BOT_SPEED * 0.5;
    const moveX = Math.cos(botYaw) * strafe;
    const moveZ = -Math.sin(botYaw) * strafe;
    const [nx, nz] = resolvePillarCollision(
      botGroup.position.x + moveX,
      botGroup.position.z + moveZ,
      0.5
    );
    botGroup.position.x = nx;
    botGroup.position.z = nz;
  }

  if (Math.abs(angleDiff) < 0.4) {
    botShoot();
  }
}

// ── Player movement ─────────────────────────────────────────────────
function updatePlayer() {
  if (keys.ArrowLeft) playerYaw += TURN_SPEED;
  if (keys.ArrowRight) playerYaw -= TURN_SPEED;

  camera.rotation.y = playerYaw;

  let moveX = 0;
  let moveZ = 0;

  if (keys.ArrowUp) {
    moveX += Math.sin(playerYaw) * PLAYER_SPEED;
    moveZ += Math.cos(playerYaw) * PLAYER_SPEED;
  }
  if (keys.ArrowDown) {
    moveX -= Math.sin(playerYaw) * PLAYER_SPEED;
    moveZ -= Math.cos(playerYaw) * PLAYER_SPEED;
  }

  if (moveX !== 0 || moveZ !== 0) {
    const [nx, nz] = resolvePillarCollision(
      camera.position.x + moveX,
      camera.position.z + moveZ
    );
    camera.position.x = nx;
    camera.position.z = nz;
  }

  if (keys.Space) {
    playerShoot();
  }
}

// ── Bullet updates & hit detection ──────────────────────────────────
function updateBullets() {
  for (let i = bullets.length - 1; i >= 0; i--) {
    const b = bullets[i];
    b.mesh.position.add(b.velocity);
    b.life--;

    const pos = b.mesh.position;
    const half = ARENA_SIZE / 2;

    // Wall collision
    if (
      Math.abs(pos.x) > half - 0.5 ||
      Math.abs(pos.z) > half - 0.5 ||
      pos.y < 0 || pos.y > WALL_HEIGHT
    ) {
      spawnImpact(pos.clone());
      scene.remove(b.mesh);
      bullets.splice(i, 1);
      continue;
    }

    // Pillar collision
    let hitPillar = false;
    for (const p of pillars) {
      const dx = pos.x - p.x;
      const dz = pos.z - p.z;
      if (dx * dx + dz * dz < p.r * p.r) {
        spawnImpact(pos.clone());
        scene.remove(b.mesh);
        bullets.splice(i, 1);
        hitPillar = true;
        break;
      }
    }
    if (hitPillar) continue;

    // Hit player
    if (!b.isPlayer) {
      const dx = pos.x - camera.position.x;
      const dz = pos.z - camera.position.z;
      const dy = pos.y - (camera.position.y - 0.3);
      if (dx * dx + dz * dz + dy * dy < 0.7) {
        spawnImpact(pos.clone(), 0xff4444);
        takeDamage(true, BULLET_DAMAGE);
        scene.remove(b.mesh);
        bullets.splice(i, 1);
        continue;
      }
    }

    // Hit bot
    if (b.isPlayer) {
      const dx = pos.x - botGroup.position.x;
      const dz = pos.z - botGroup.position.z;
      const dy = pos.y - 1.5;
      if (dx * dx + dz * dz + dy * dy < 1.0) {
        spawnImpact(pos.clone(), 0xff6644);
        takeDamage(false, BULLET_DAMAGE);
        scene.remove(b.mesh);
        bullets.splice(i, 1);
        continue;
      }
    }

    if (b.life <= 0) {
      scene.remove(b.mesh);
      bullets.splice(i, 1);
    }
  }
}

function updateParticles() {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.mesh.position.add(p.velocity);
    p.velocity.y -= 0.003;
    p.life--;
    p.mesh.scale.multiplyScalar(0.92);
    if (p.life <= 0) {
      scene.remove(p.mesh);
      particles.splice(i, 1);
    }
  }
}

// ── Input ───────────────────────────────────────────────────────────
window.addEventListener("keydown", (e) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) {
    e.preventDefault();
    keys[e.code] = true;
  }
});

window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

window.addEventListener("blur", () => {
  Object.keys(keys).forEach((k) => { keys[k] = false; });
});

startBtn.addEventListener("click", () => {
  startScreen.classList.add("hidden");
  resetGame();
});

restartBtn.addEventListener("click", resetGame);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ── Game loop ───────────────────────────────────────────────────────
camera.rotation.order = "YXZ";
updateHealthUI();

function animate() {
  requestAnimationFrame(animate);

  if (gameRunning) {
    updatePlayer();
    updateBot();
    updateBullets();
  }
  updateParticles();

  // Subtle weapon bob
  if (gameRunning && (keys.ArrowUp || keys.ArrowDown)) {
    weaponGroup.position.y = -0.15 + Math.sin(performance.now() * 0.012) * 0.02;
  }

  // Enemy glow pulse
  const pulse = 0.55 + Math.sin(performance.now() * 0.006) * 0.45;
  enemyGlowParts.forEach((mat) => {
    mat.color.setRGB(1, 0.13 * pulse, 0);
  });

  renderer.render(scene, camera);
}

animate();
