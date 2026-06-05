import * as THREE from "three";
import {
  ARENA_SIZE,
  WALL_HEIGHT,
  PILLAR_POSITIONS,
  ENVIRONMENTS,
  buildWorld,
  applyEnvironmentLighting,
} from "./environments.js";

// ── Config ──────────────────────────────────────────────────────────
const PLAYER_SPEED = 0.16;
const TURN_SPEED = 0.042;
const BULLET_SPEED = 1.15;

const DIFFICULTY_PRESETS = {
  normal: {
    label: "NORMAL",
    description: "Standard hostile — moderate speed and accuracy.",
    maxHp: 100,
    enemyMaxHp: 100,
    playerDamage: 20,
    enemyDamage: 18,
    fireCooldown: 380,
    magSize: 12,
    reserveAmmo: 48,
    reloadTime: 1600,
    botSpeed: 0.11,
    botTurnSpeed: 0.038,
    botFireRange: 24,
    botFireCooldown: 720,
    botBurstSize: 2,
    botBurstPause: 1100,
    botAccuracy: 0.78,
    enemyBulletSpeed: 1.2,
  },
  hard: {
    label: "HARD",
    description: "Elite hostile — faster, tougher, burst fire, uses cover.",
    maxHp: 80,
    enemyMaxHp: 130,
    playerDamage: 16,
    enemyDamage: 24,
    fireCooldown: 420,
    magSize: 10,
    reserveAmmo: 40,
    reloadTime: 2000,
    botSpeed: 0.15,
    botTurnSpeed: 0.05,
    botFireRange: 30,
    botFireCooldown: 480,
    botBurstSize: 3,
    botBurstPause: 1300,
    botAccuracy: 0.91,
    enemyBulletSpeed: 1.5,
  },
};

let difficulty = "hard";
let cfg = { ...DIFFICULTY_PRESETS.hard };
let currentEnvironment = "city";
let activeEnv = ENVIRONMENTS.city;

// ── State ───────────────────────────────────────────────────────────
const keys = {};
let gameRunning = false;
let gamePaused = false;
let playerHP = cfg.maxHp;
let enemyHP = cfg.enemyMaxHp;
let kills = 0;
let lastPlayerShot = 0;
let lastBotShot = 0;
let playerYaw = 0;
let botYaw = Math.PI;
let magAmmo = cfg.magSize;
let reserveAmmo = cfg.reserveAmmo;
let isReloading = false;
let reloadStart = 0;
let gameStartTime = 0;
let botBurstCount = 0;
let botBurstPauseUntil = 0;
let botStrafeDir = 1;
let lastBotStrafeSwitch = 0;
let damageVignetteTimeout = 0;
let hitMarkerTimeout = 0;
let hudMessageTimeout = 0;
let prevPlayerX = 0;
let prevPlayerZ = 0;
let shotsFired = 0;
let shotsHit = 0;
let damageTaken = 0;

const bullets = [];
const particles = [];

// ── DOM ─────────────────────────────────────────────────────────────
const startScreen = document.getElementById("start-screen");
const gameOverScreen = document.getElementById("game-over");
const pauseScreen = document.getElementById("pause-screen");
const startBtn = document.getElementById("start-btn");
const restartBtn = document.getElementById("restart-btn");
const resumeBtn = document.getElementById("resume-btn");
const quitBtn = document.getElementById("quit-btn");
const uiLayer = document.getElementById("ui");
const vitalsPanel = document.getElementById("vitals-panel");
const playerHealthBar = document.getElementById("player-health");
const enemyHealthBar = document.getElementById("enemy-health");
const playerHpText = document.getElementById("player-hp-text");
const enemyHpText = document.getElementById("enemy-hp-text");
const killsEl = document.getElementById("kills");
const ammoFlash = document.getElementById("ammo-flash");
const resultTitle = document.getElementById("result-title");
const resultMessage = document.getElementById("result-message");
const resultStats = document.getElementById("result-stats");
const missionTimer = document.getElementById("mission-timer");
const threatLevel = document.getElementById("threat-level");
const hudDifficulty = document.getElementById("hud-difficulty");
const ammoCurrent = document.getElementById("ammo-current");
const ammoReserve = document.getElementById("ammo-reserve");
const reloadBarWrap = document.getElementById("reload-bar-wrap");
const reloadBar = document.getElementById("reload-bar");
const weaponStatus = document.getElementById("weapon-status");
const enemyDistance = document.getElementById("enemy-distance");
const enemyLos = document.getElementById("enemy-los");
const crosshair = document.getElementById("crosshair");
const hitMarker = document.getElementById("hit-marker");
const damageVignette = document.getElementById("damage-vignette");
const hudMessage = document.getElementById("hud-message");
const enemyPointer = document.getElementById("enemy-pointer");
const enemyPointerArrow = document.getElementById("enemy-pointer-arrow");
const enemyPointerDist = document.getElementById("enemy-pointer-dist");
const minimapCanvas = document.getElementById("minimap");
const minimapCtx = minimapCanvas.getContext("2d");
const diffDescription = document.getElementById("diff-description");
const diffButtons = document.querySelectorAll(".diff-btn");
const mapDescription = document.getElementById("map-description");
const mapButtons = document.querySelectorAll(".map-btn");
const hudField = document.getElementById("hud-field");

// ── Three.js setup ──────────────────────────────────────────────────
const scene = new THREE.Scene();

const arenaGroup = new THREE.Group();
const surroundingsGroup = new THREE.Group();
scene.add(surroundingsGroup);
scene.add(arenaGroup);

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

const worldLights = { ambient, sun, rim1: rimLight, rim2: rimLight2 };

// ── World / arena ───────────────────────────────────────────────────
const pillars = PILLAR_POSITIONS.map(([x, z]) => ({ x, z, r: 1.8 }));

function applyEnvironment(mode) {
  currentEnvironment = mode;
  activeEnv = buildWorld(mode, arenaGroup, surroundingsGroup);
  applyEnvironmentLighting(scene, activeEnv, worldLights);
  hudField.textContent = activeEnv.label;
  mapDescription.textContent = activeEnv.description;
  mapButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.map === mode);
  });
}

applyEnvironment(currentEnvironment);

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

function applyDifficulty(mode) {
  difficulty = mode;
  cfg = { ...DIFFICULTY_PRESETS[mode] };
  hudDifficulty.textContent = cfg.label;
  diffDescription.textContent = cfg.description;
  diffButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.diff === mode);
  });
}

function selectEnvironment(mode) {
  if (ENVIRONMENTS[mode]) applyEnvironment(mode);
}

function togglePause(force) {
  if (!gameRunning) return;
  gamePaused = force !== undefined ? force : !gamePaused;
  pauseScreen.classList.toggle("hidden", !gamePaused);
  uiLayer.classList.toggle("paused", gamePaused);
  if (gamePaused) {
    Object.keys(keys).forEach((k) => { keys[k] = false; });
  }
}

function returnToMenu() {
  gameRunning = false;
  gamePaused = false;
  pauseScreen.classList.add("hidden");
  gameOverScreen.classList.add("hidden");
  startScreen.classList.remove("hidden");
  uiLayer.classList.add("menu-open");
  uiLayer.classList.remove("paused");
  bullets.forEach((b) => scene.remove(b.mesh));
  bullets.length = 0;
}

function startReload() {
  if (isReloading || magAmmo >= cfg.magSize || reserveAmmo <= 0) return;
  isReloading = true;
  reloadStart = performance.now();
  reloadBarWrap.classList.remove("hidden");
  weaponStatus.textContent = "RELOADING";
  weaponStatus.className = "weapon-status reloading";
  showHudMessage("RELOADING...");
}

function finishReload() {
  const needed = cfg.magSize - magAmmo;
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
  const progress = Math.min(1, (now - reloadStart) / cfg.reloadTime);
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

  if (now - lastPlayerShot < cfg.fireCooldown) return;
  lastPlayerShot = now;
  magAmmo--;
  shotsFired++;

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
  if (now < botBurstPauseUntil) return;
  if (now - lastBotShot < cfg.botFireCooldown) return;

  const toPlayer = new THREE.Vector3(
    camera.position.x - botGroup.position.x,
    0,
    camera.position.z - botGroup.position.z
  );
  const dist = toPlayer.length();
  if (dist > cfg.botFireRange) return;

  lastBotShot = now;
  botBurstCount++;
  if (botBurstCount >= cfg.botBurstSize) {
    botBurstCount = 0;
    botBurstPauseUntil = now + cfg.botBurstPause;
  }

  // Lead target based on player movement
  const playerVelX = camera.position.x - prevPlayerX;
  const playerVelZ = camera.position.z - prevPlayerZ;
  const leadTime = dist / cfg.enemyBulletSpeed;
  const predictedX = camera.position.x + playerVelX * leadTime * 8;
  const predictedZ = camera.position.z + playerVelZ * leadTime * 8;

  const direction = new THREE.Vector3(
    predictedX - botGroup.position.x,
    0,
    predictedZ - botGroup.position.z
  ).normalize();
  direction.y = (camera.position.y - 1.5) / dist;

  if (Math.random() > cfg.botAccuracy) {
    direction.x += (Math.random() - 0.5) * 0.18;
    direction.z += (Math.random() - 0.5) * 0.18;
    direction.y += (Math.random() - 0.5) * 0.1;
  }

  const origin = new THREE.Vector3(
    botGroup.position.x + direction.x * 0.5,
    1.5,
    botGroup.position.z + direction.z * 0.5
  );

  spawnBullet(origin, direction, false, cfg.enemyBulletSpeed);
}

// ── Damage & UI ─────────────────────────────────────────────────────
function formatTime(ms) {
  const totalSec = Math.floor(ms / 1000);
  const m = String(Math.floor(totalSec / 60)).padStart(2, "0");
  const s = String(totalSec % 60).padStart(2, "0");
  return `${m}:${s}`;
}

function getEnemyDistance() {
  const dx = camera.position.x - botGroup.position.x;
  const dz = camera.position.z - botGroup.position.z;
  return Math.sqrt(dx * dx + dz * dz);
}

function updateThreat(dist) {
  threatLevel.classList.remove("threat-low", "threat-med", "threat-high");
  if (dist < 10) {
    threatLevel.textContent = "CRITICAL";
    threatLevel.classList.add("threat-high");
  } else if (dist < 18) {
    threatLevel.textContent = "HIGH";
    threatLevel.classList.add("threat-med");
  } else {
    threatLevel.textContent = "MODERATE";
    threatLevel.classList.add("threat-low");
  }
}

function drawMinimap() {
  const w = minimapCanvas.width;
  const h = minimapCanvas.height;
  const scale = w / ARENA_SIZE;

  minimapCtx.fillStyle = "rgba(0, 12, 24, 0.9)";
  minimapCtx.fillRect(0, 0, w, h);

  minimapCtx.strokeStyle = "rgba(102, 204, 255, 0.2)";
  minimapCtx.lineWidth = 1;
  minimapCtx.strokeRect(4, 4, w - 8, h - 8);

  // Pillars
  minimapCtx.fillStyle = "rgba(80, 80, 110, 0.8)";
  pillars.forEach((p) => {
    const px = w / 2 + p.x * scale;
    const py = h / 2 + p.z * scale;
    minimapCtx.fillRect(px - 4, py - 4, 8, 8);
  });

  // Enemy
  const ex = w / 2 + botGroup.position.x * scale;
  const ey = h / 2 + botGroup.position.z * scale;
  minimapCtx.fillStyle = "#ff4444";
  minimapCtx.beginPath();
  minimapCtx.arc(ex, ey, 5, 0, Math.PI * 2);
  minimapCtx.fill();

  // Player
  const px = w / 2 + camera.position.x * scale;
  const py = h / 2 + camera.position.z * scale;
  minimapCtx.fillStyle = "#44ddff";
  minimapCtx.beginPath();
  minimapCtx.moveTo(px, py - 6);
  minimapCtx.lineTo(px + 4, py + 4);
  minimapCtx.lineTo(px - 4, py + 4);
  minimapCtx.closePath();
  minimapCtx.fill();

  // Player facing
  minimapCtx.strokeStyle = "#44ddff";
  minimapCtx.lineWidth = 2;
  minimapCtx.beginPath();
  minimapCtx.moveTo(px, py);
  minimapCtx.lineTo(px + Math.sin(playerYaw) * 12, py + Math.cos(playerYaw) * 12);
  minimapCtx.stroke();
}

function updateEnemyPointer(dist) {
  const dx = botGroup.position.x - camera.position.x;
  const dz = botGroup.position.z - camera.position.z;
  const angleToEnemy = Math.atan2(dx, dz);
  const relAngle = angleToEnemy - playerYaw;

  const forward = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
  const toEnemy = new THREE.Vector3(dx, 0, dz).normalize();
  const dot = forward.dot(toEnemy);

  if (dot > 0.25) {
    enemyPointer.classList.add("hidden");
    return;
  }

  enemyPointer.classList.remove("hidden");
  const edgePad = 80;
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  const px = cx + Math.sin(relAngle) * (Math.min(cx, cy) - edgePad);
  const py = cy - Math.cos(relAngle) * (Math.min(cx, cy) - edgePad);

  enemyPointer.style.left = `${px}px`;
  enemyPointer.style.top = `${py}px`;
  enemyPointerArrow.style.transform = `rotate(${relAngle * (180 / Math.PI)}deg)`;
  enemyPointerDist.textContent = `${Math.round(dist)}m`;
}

function updateHUD(now) {
  const dist = getEnemyDistance();

  playerHealthBar.style.width = `${(playerHP / cfg.maxHp) * 100}%`;
  enemyHealthBar.style.width = `${(enemyHP / cfg.enemyMaxHp) * 100}%`;
  playerHpText.textContent = Math.max(0, playerHP);
  enemyHpText.textContent = Math.max(0, enemyHP);
  enemyDistance.textContent = `${Math.round(dist)} m`;
  ammoCurrent.textContent = magAmmo;
  ammoReserve.textContent = reserveAmmo;

  if (gameRunning) {
    missionTimer.textContent = formatTime(now - gameStartTime);
  }

  updateThreat(dist);
  drawMinimap();
  updateEnemyPointer(dist);

  const moving = keys.ArrowUp || keys.ArrowDown;
  const onCooldown = now - lastPlayerShot < cfg.fireCooldown;
  crosshair.classList.toggle("spread", moving);
  crosshair.classList.toggle("cooldown", onCooldown || isReloading);

  vitalsPanel.classList.toggle("critical", playerHP > 0 && playerHP <= cfg.maxHp * 0.25);

  const los = hasLineOfSight();
  enemyLos.textContent = los ? "IN SIGHT" : "BEHIND COVER";
  enemyLos.className = los ? "los-clear" : "los-blocked";

  if (!isReloading) {
    if (magAmmo === 0) {
      weaponStatus.textContent = "EMPTY";
      weaponStatus.className = "weapon-status empty";
    } else {
      weaponStatus.textContent = "READY";
      weaponStatus.className = "weapon-status";
    }
  }
}

function updateHealthUI() {
  updateHUD(performance.now());
}

function takeDamage(isPlayer, amount) {
  if (isPlayer) {
    playerHP = Math.max(0, playerHP - amount);
    damageTaken += amount;
    flashDamage();
    if (playerHP > 0 && playerHP <= cfg.maxHp * 0.25) {
      showHudMessage("CRITICAL DAMAGE — SEEK COVER", 1500);
    }
  } else {
    enemyHP = Math.max(0, enemyHP - amount);
    shotsHit++;
    showHitMarker();
  }
  updateHealthUI();

  if (playerHP <= 0 || enemyHP <= 0) {
    endGame(enemyHP <= 0);
  }
}

function renderResultStats(victory) {
  const elapsed = performance.now() - gameStartTime;
  const accuracy = shotsFired > 0 ? Math.round((shotsHit / shotsFired) * 100) : 0;
  resultStats.innerHTML = `
    <div class="stat-item"><span class="stat-label">TIME</span><span class="stat-value">${formatTime(elapsed)}</span></div>
    <div class="stat-item"><span class="stat-label">FIELD</span><span class="stat-value">${activeEnv.label}</span></div>
    <div class="stat-item"><span class="stat-label">DIFFICULTY</span><span class="stat-value">${cfg.label}</span></div>
    <div class="stat-item"><span class="stat-label">SHOTS FIRED</span><span class="stat-value">${shotsFired}</span></div>
    <div class="stat-item"><span class="stat-label">ACCURACY</span><span class="stat-value">${accuracy}%</span></div>
    <div class="stat-item"><span class="stat-label">HITS LANDED</span><span class="stat-value">${shotsHit}</span></div>
    <div class="stat-item"><span class="stat-label">DAMAGE TAKEN</span><span class="stat-value">${damageTaken}</span></div>
  `;
}

function endGame(victory) {
  gameRunning = false;
  gamePaused = false;
  pauseScreen.classList.add("hidden");
  uiLayer.classList.remove("paused");
  gameOverScreen.classList.remove("hidden", "victory", "defeat");
  gameOverScreen.classList.add(victory ? "victory" : "defeat");
  resultTitle.textContent = victory ? "Victory!" : "Defeated";
  resultMessage.textContent = victory
    ? "You eliminated the elite hostile."
    : "The hostile overwhelmed your defenses. Try again!";
  renderResultStats(victory);
  if (victory) {
    kills++;
    killsEl.textContent = kills;
  }
}

function resetGame() {
  applyDifficulty(difficulty);
  applyEnvironment(currentEnvironment);
  playerHP = cfg.maxHp;
  enemyHP = cfg.enemyMaxHp;
  playerYaw = 0;
  botYaw = Math.PI;
  lastPlayerShot = 0;
  lastBotShot = 0;
  magAmmo = cfg.magSize;
  reserveAmmo = cfg.reserveAmmo;
  isReloading = false;
  botBurstCount = 0;
  botBurstPauseUntil = 0;
  botStrafeDir = 1;
  gameStartTime = performance.now();
  shotsFired = 0;
  shotsHit = 0;
  damageTaken = 0;
  gamePaused = false;

  camera.position.set(0, 1.7, 12);
  camera.rotation.set(0, 0, 0);
  camera.rotation.order = "YXZ";
  prevPlayerX = camera.position.x;
  prevPlayerZ = camera.position.z;

  botGroup.position.set(0, 0, -12);
  botGroup.rotation.y = 0;

  bullets.forEach((b) => scene.remove(b.mesh));
  bullets.length = 0;
  particles.forEach((p) => scene.remove(p.mesh));
  particles.length = 0;

  reloadBarWrap.classList.add("hidden");
  reloadBar.style.width = "0%";
  weaponStatus.textContent = "READY";
  weaponStatus.className = "weapon-status";
  enemyPointer.classList.add("hidden");

  updateHealthUI();
  showHudMessage(`${activeEnv.label} — HOSTILE DETECTED`, 2500);
  gameOverScreen.classList.add("hidden");
  pauseScreen.classList.add("hidden");
  startScreen.classList.add("hidden");
  uiLayer.classList.remove("menu-open", "paused");
  gameRunning = true;
}

// ── Bot AI ──────────────────────────────────────────────────────────
function hasLineOfSight() {
  const steps = 12;
  const dx = (camera.position.x - botGroup.position.x) / steps;
  const dz = (camera.position.z - botGroup.position.z) / steps;
  let x = botGroup.position.x;
  let z = botGroup.position.z;

  for (let i = 1; i < steps; i++) {
    x += dx;
    z += dz;
    for (const p of pillars) {
      const pdx = x - p.x;
      const pdz = z - p.z;
      if (pdx * pdx + pdz * pdz < p.r * p.r) return false;
    }
  }
  return true;
}

function findCoverDirection() {
  let bestScore = Infinity;
  let bestAngle = botYaw;

  for (let i = 0; i < 8; i++) {
    const testAngle = botYaw + (i / 8) * Math.PI * 2;
    const tx = botGroup.position.x + Math.sin(testAngle) * 4;
    const tz = botGroup.position.z + Math.cos(testAngle) * 4;
    const [nx, nz] = resolvePillarCollision(tx, tz, 0.5);

    let blocked = false;
    const pdx = camera.position.x - nx;
    const pdz = camera.position.z - nz;
    const steps = 6;
    for (let s = 1; s <= steps; s++) {
      const sx = nx + (pdx / steps) * s;
      const sz = nz + (pdz / steps) * s;
      for (const p of pillars) {
        const ddx = sx - p.x;
        const ddz = sz - p.z;
        if (ddx * ddx + ddz * ddz < p.r * p.r) {
          blocked = true;
          break;
        }
      }
      if (blocked) break;
    }

    const distToPlayer = Math.hypot(nx - camera.position.x, nz - camera.position.z);
    const score = blocked ? distToPlayer : distToPlayer + 20;
    if (score < bestScore) {
      bestScore = score;
      bestAngle = Math.atan2(nx - botGroup.position.x, nz - botGroup.position.z);
    }
  }
  return bestAngle;
}

function updateBot() {
  const dx = camera.position.x - botGroup.position.x;
  const dz = camera.position.z - botGroup.position.z;
  const dist = Math.sqrt(dx * dx + dz * dz);
  const los = hasLineOfSight();
  const now = performance.now();

  let targetAngle;
  if (los && dist < 14 && playerHP > 30) {
    targetAngle = findCoverDirection();
  } else {
    targetAngle = Math.atan2(dx, dz);
  }

  let angleDiff = targetAngle - botYaw;
  while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
  while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;

  botYaw += Math.sign(angleDiff) * Math.min(Math.abs(angleDiff), cfg.botTurnSpeed);
  botGroup.rotation.y = botYaw + Math.PI;

  const idealDist = 8;
  const speedMult = dist < 12 ? 1.15 : 1;

  if (now - lastBotStrafeSwitch > 1800) {
    botStrafeDir *= -1;
    lastBotStrafeSwitch = now;
  }

  if (dist > idealDist + 1.5) {
    const moveX = Math.sin(botYaw) * cfg.botSpeed * speedMult;
    const moveZ = Math.cos(botYaw) * cfg.botSpeed * speedMult;
    const [nx, nz] = resolvePillarCollision(
      botGroup.position.x + moveX,
      botGroup.position.z + moveZ,
      0.5
    );
    botGroup.position.x = nx;
    botGroup.position.z = nz;
  } else if (dist < idealDist - 2) {
    const moveX = -Math.sin(botYaw) * cfg.botSpeed * 0.85;
    const moveZ = -Math.cos(botYaw) * cfg.botSpeed * 0.85;
    const [nx, nz] = resolvePillarCollision(
      botGroup.position.x + moveX,
      botGroup.position.z + moveZ,
      0.5
    );
    botGroup.position.x = nx;
    botGroup.position.z = nz;
  } else {
    const strafe = botStrafeDir * cfg.botSpeed * 0.75;
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

  const aimDiff = Math.atan2(dx, dz) - botYaw;
  let normAim = aimDiff;
  while (normAim > Math.PI) normAim -= Math.PI * 2;
  while (normAim < -Math.PI) normAim += Math.PI * 2;

  if (Math.abs(normAim) < 0.35 && los) {
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
        takeDamage(true, cfg.enemyDamage);
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
        takeDamage(false, cfg.playerDamage);
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
  if (e.code === "KeyP" || e.code === "Escape") {
    e.preventDefault();
    if (gameRunning) togglePause();
    return;
  }

  if (e.code === "KeyR" && gameRunning && !gamePaused) {
    e.preventDefault();
    startReload();
    return;
  }

  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) {
    e.preventDefault();
    if (gameRunning && !gamePaused) keys[e.code] = true;
  }
});

window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

window.addEventListener("blur", () => {
  Object.keys(keys).forEach((k) => { keys[k] = false; });
  if (gameRunning) togglePause(true);
});

diffButtons.forEach((btn) => {
  btn.addEventListener("click", () => applyDifficulty(btn.dataset.diff));
});

mapButtons.forEach((btn) => {
  btn.addEventListener("click", () => selectEnvironment(btn.dataset.map));
});

startBtn.addEventListener("click", () => {
  resetGame();
});

restartBtn.addEventListener("click", resetGame);

resumeBtn.addEventListener("click", () => togglePause(false));

quitBtn.addEventListener("click", returnToMenu);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// ── Game loop ───────────────────────────────────────────────────────
camera.rotation.order = "YXZ";
applyDifficulty(difficulty);
updateHealthUI();

function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();

  if (gameRunning && !gamePaused) {
    prevPlayerX = camera.position.x;
    prevPlayerZ = camera.position.z;
    updateReload(now);
    updatePlayer();
    updateBot();
    updateBullets();
    updateHUD(now);
  }
  updateParticles();

  // Subtle weapon bob
  if (gameRunning && !gamePaused && (keys.ArrowUp || keys.ArrowDown)) {
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
