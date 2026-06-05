import * as THREE from "three";

export const ARENA_SIZE = 40;
export const WALL_HEIGHT = 6;

export const PILLAR_POSITIONS = [
  [-8, 0, -8], [8, 0, -8], [-8, 0, 8], [8, 0, 8],
  [0, 0, 0], [-12, 0, 0], [12, 0, 0], [0, 0, -12], [0, 0, 12],
];

function addShadow(mesh) {
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function disposeMesh(mesh) {
  if (mesh.geometry) mesh.geometry.dispose();
  if (mesh.material) {
    if (Array.isArray(mesh.material)) mesh.material.forEach((m) => m.dispose());
    else mesh.material.dispose();
  }
}

export function disposeGroup(group) {
  const children = [...group.children];
  children.forEach((child) => {
    group.remove(child);
    if (child.isGroup) {
      disposeGroup(child);
    } else {
      disposeMesh(child);
    }
  });
}

function buildOuterGround(group, color, size = 120) {
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(size, size),
    new THREE.MeshStandardMaterial({ color, roughness: 0.95, metalness: 0.02 })
  );
  ground.rotation.x = -Math.PI / 2;
  ground.position.y = -0.02;
  ground.receiveShadow = true;
  group.add(ground);
}

function buildArenaCore(group, env) {
  const half = ARENA_SIZE / 2;

  const floor = addShadow(new THREE.Mesh(
    new THREE.PlaneGeometry(ARENA_SIZE, ARENA_SIZE, 20, 20),
    new THREE.MeshStandardMaterial({
      color: env.floor.color,
      roughness: env.floor.roughness ?? 0.85,
      metalness: env.floor.metalness ?? 0.1,
    })
  ));
  floor.rotation.x = -Math.PI / 2;
  group.add(floor);

  if (env.floor.grid) {
    const grid = new THREE.GridHelper(
      ARENA_SIZE, 20,
      env.floor.gridPrimary ?? 0x334466,
      env.floor.gridSecondary ?? 0x222233
    );
    grid.position.y = 0.01;
    group.add(grid);
  }

  const wallMat = new THREE.MeshStandardMaterial({
    color: env.walls.color,
    roughness: env.walls.roughness ?? 0.75,
    metalness: env.walls.metalness ?? 0.2,
  });
  const wallGeo = new THREE.BoxGeometry(ARENA_SIZE, WALL_HEIGHT, 0.8);
  const wallDefs = [
    { pos: [0, WALL_HEIGHT / 2, -half], rot: 0 },
    { pos: [0, WALL_HEIGHT / 2, half], rot: 0 },
    { pos: [-half, WALL_HEIGHT / 2, 0], rot: Math.PI / 2 },
    { pos: [half, WALL_HEIGHT / 2, 0], rot: Math.PI / 2 },
  ];

  wallDefs.forEach(({ pos, rot }) => {
    const wall = addShadow(new THREE.Mesh(wallGeo, wallMat));
    wall.position.set(...pos);
    wall.rotation.y = rot;
    group.add(wall);

    if (env.walls.trimColor != null) {
      const trim = new THREE.Mesh(
        new THREE.BoxGeometry(ARENA_SIZE, 0.15, 0.2),
        new THREE.MeshBasicMaterial({ color: env.walls.trimColor })
      );
      trim.position.set(pos[0], 0.3, pos[2]);
      trim.rotation.y = rot;
      group.add(trim);
    }
  });

  PILLAR_POSITIONS.forEach(([x, , z]) => {
    let pillar;
    if (env.pillars.style === "rock") {
      pillar = addShadow(new THREE.Mesh(
        new THREE.DodecahedronGeometry(1.4, 0),
        new THREE.MeshStandardMaterial({ color: env.pillars.color, roughness: 0.95, flatShading: true })
      ));
      pillar.scale.set(1.2, 2.2, 1.2);
    } else if (env.pillars.style === "crate") {
      pillar = addShadow(new THREE.Mesh(
        new THREE.BoxGeometry(2.5, 2.5, 2.5),
        new THREE.MeshStandardMaterial({ color: env.pillars.color, roughness: 0.8 })
      ));
    } else if (env.pillars.style === "palm") {
      const trunk = addShadow(new THREE.Mesh(
        new THREE.CylinderGeometry(0.25, 0.35, 3.2, 6),
        new THREE.MeshStandardMaterial({ color: 0x6b4a2a, roughness: 0.9 })
      ));
      trunk.position.y = 1.6;
      const leaves = addShadow(new THREE.Mesh(
        new THREE.ConeGeometry(1.6, 2.2, 6),
        new THREE.MeshStandardMaterial({ color: env.pillars.color, roughness: 0.85, flatShading: true })
      ));
      leaves.position.y = 3.6;
      pillar = new THREE.Group();
      pillar.add(trunk, leaves);
    } else {
      pillar = addShadow(new THREE.Mesh(
        new THREE.BoxGeometry(2.5, 3.5, 2.5),
        new THREE.MeshStandardMaterial({
          color: env.pillars.color,
          roughness: 0.6,
          metalness: env.pillars.metalness ?? 0.3,
        })
      ));
    }
    pillar.position.set(x, env.pillars.style === "palm" ? 0 : 1.75, z);
    group.add(pillar);
  });
}

function buildCityscape(group) {
  buildOuterGround(group, 0x1a2030, 140);

  for (let i = 0; i < 28; i++) {
    const angle = (i / 28) * Math.PI * 2;
    const dist = 28 + (i % 5) * 3;
    const w = 2.5 + (i % 4) * 1.2;
    const d = 2.5 + (i % 3) * 1.5;
    const h = 10 + (i % 7) * 4;

    const building = addShadow(new THREE.Mesh(
      new THREE.BoxGeometry(w, h, d),
      new THREE.MeshStandardMaterial({
        color: i % 3 === 0 ? 0x2a3548 : 0x1e2838,
        roughness: 0.65,
        metalness: 0.35,
      })
    ));
    building.position.set(Math.sin(angle) * dist, h / 2, Math.cos(angle) * dist);
    building.rotation.y = angle;
    group.add(building);

    const rows = Math.floor(h / 2.5);
    for (let r = 1; r < rows; r++) {
      for (let c = 0; c < 2; c++) {
        if (Math.random() > 0.35) {
          const win = new THREE.Mesh(
            new THREE.PlaneGeometry(0.5, 0.7),
            new THREE.MeshBasicMaterial({
              color: Math.random() > 0.5 ? 0xffcc66 : 0x66ccff,
              transparent: true,
              opacity: 0.7 + Math.random() * 0.3,
            })
          );
          win.position.set(
            building.position.x + Math.sin(angle) * (d / 2 + 0.05),
            r * 2.2,
            building.position.z + Math.cos(angle) * (d / 2 + 0.05)
          );
          win.rotation.y = angle;
          group.add(win);
        }
      }
    }
  }

  // Distant skyline
  for (let i = 0; i < 12; i++) {
    const x = -55 + i * 10;
    const h = 18 + (i % 4) * 8;
    const tower = addShadow(new THREE.Mesh(
      new THREE.BoxGeometry(6, h, 5),
      new THREE.MeshStandardMaterial({ color: 0x151c28, roughness: 0.8 })
    ));
    tower.position.set(x, h / 2, -58);
    group.add(tower);
  }
}

function buildJungle(group) {
  buildOuterGround(group, 0x1a3d1a, 140);

  for (let i = 0; i < 45; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 24 + Math.random() * 22;
    const x = Math.sin(angle) * dist;
    const z = Math.cos(angle) * dist;
    const scale = 0.7 + Math.random() * 1.4;

    const tree = new THREE.Group();
    const trunk = addShadow(new THREE.Mesh(
      new THREE.CylinderGeometry(0.2 * scale, 0.35 * scale, 3 * scale, 6),
      new THREE.MeshStandardMaterial({ color: 0x4a3020, roughness: 0.95 })
    ));
    trunk.position.y = 1.5 * scale;
    tree.add(trunk);

    for (let l = 0; l < 3; l++) {
      const foliage = addShadow(new THREE.Mesh(
        new THREE.ConeGeometry(1.5 * scale, 2.5 * scale, 7),
        new THREE.MeshStandardMaterial({
          color: l === 0 ? 0x1f6b1f : 0x2d8a2d,
          roughness: 0.9,
          flatShading: true,
        })
      ));
      foliage.position.y = (2.5 + l * 1.4) * scale;
      tree.add(foliage);
    }

    tree.position.set(x, 0, z);
    group.add(tree);
  }

  // Undergrowth rings
  for (let i = 0; i < 30; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 22 + Math.random() * 8;
    const bush = addShadow(new THREE.Mesh(
      new THREE.SphereGeometry(0.8 + Math.random(), 6, 5),
      new THREE.MeshStandardMaterial({ color: 0x256325, roughness: 0.95, flatShading: true })
    ));
    bush.position.set(Math.sin(angle) * dist, 0.5, Math.cos(angle) * dist);
    bush.scale.y = 0.7;
    group.add(bush);
  }
}

function buildMountains(group) {
  buildOuterGround(group, 0x3d4a35, 160);

  const mountainData = [
    { x: -45, z: -55, h: 28, r: 14, color: 0x4a5568 },
    { x: -20, z: -58, h: 35, r: 18, color: 0x5a6578 },
    { x: 10, z: -60, h: 42, r: 22, color: 0x6a7588 },
    { x: 35, z: -56, h: 30, r: 16, color: 0x4a5568 },
    { x: 55, z: -52, h: 24, r: 12, color: 0x556070 },
    { x: -55, z: 40, h: 22, r: 11, color: 0x4a5548 },
    { x: 50, z: 45, h: 26, r: 13, color: 0x525d50 },
  ];

  mountainData.forEach(({ x, z, h, r, color }) => {
    const mountain = addShadow(new THREE.Mesh(
      new THREE.ConeGeometry(r, h, 8),
      new THREE.MeshStandardMaterial({ color, roughness: 0.95, flatShading: true })
    ));
    mountain.position.set(x, h / 2 - 2, z);
    group.add(mountain);

    const snow = new THREE.Mesh(
      new THREE.ConeGeometry(r * 0.35, h * 0.22, 8),
      new THREE.MeshStandardMaterial({ color: 0xeef4ff, roughness: 0.85, flatShading: true })
    );
    snow.position.set(x, h - h * 0.1, z);
    group.add(snow);
  });

  // Pine trees
  for (let i = 0; i < 22; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 24 + Math.random() * 14;
    const pine = new THREE.Group();
    const trunk = addShadow(new THREE.Mesh(
      new THREE.CylinderGeometry(0.15, 0.25, 2, 5),
      new THREE.MeshStandardMaterial({ color: 0x3d2817, roughness: 0.95 })
    ));
    trunk.position.y = 1;
    pine.add(trunk);
    for (let t = 0; t < 4; t++) {
      const tier = addShadow(new THREE.Mesh(
        new THREE.ConeGeometry(1.3 - t * 0.2, 1.8, 6),
        new THREE.MeshStandardMaterial({ color: 0x1e4d2e, roughness: 0.9, flatShading: true })
      ));
      tier.position.y = 1.8 + t * 1.2;
      pine.add(tier);
    }
    pine.position.set(Math.sin(angle) * dist, 0, Math.cos(angle) * dist);
    group.add(pine);
  }

  // Boulders
  for (let i = 0; i < 14; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 22 + Math.random() * 6;
    const rock = addShadow(new THREE.Mesh(
      new THREE.DodecahedronGeometry(0.8 + Math.random() * 0.6, 0),
      new THREE.MeshStandardMaterial({ color: 0x5a6068, roughness: 0.95, flatShading: true })
    ));
    rock.position.set(Math.sin(angle) * dist, 0.4, Math.cos(angle) * dist);
    rock.scale.y = 0.7;
    group.add(rock);
  }
}

function buildDesert(group) {
  buildOuterGround(group, 0xc4a574, 160);

  // Dunes
  for (let i = 0; i < 10; i++) {
    const angle = (i / 10) * Math.PI * 2;
    const dist = 38 + (i % 3) * 6;
    const dune = addShadow(new THREE.Mesh(
      new THREE.SphereGeometry(6 + (i % 4) * 2, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2),
      new THREE.MeshStandardMaterial({ color: 0xd4b483, roughness: 0.98 })
    ));
    dune.position.set(Math.sin(angle) * dist, -0.5, Math.cos(angle) * dist);
    dune.scale.set(1.8, 0.7, 1.4);
    group.add(dune);
  }

  // Cacti
  for (let i = 0; i < 18; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 24 + Math.random() * 18;
    const cactus = new THREE.Group();
    const body = addShadow(new THREE.Mesh(
      new THREE.CylinderGeometry(0.35, 0.4, 2.5 + Math.random(), 8),
      new THREE.MeshStandardMaterial({ color: 0x3d7a3d, roughness: 0.85 })
    ));
    body.position.y = 1.25;
    cactus.add(body);
    if (Math.random() > 0.4) {
      const arm = addShadow(new THREE.Mesh(
        new THREE.CylinderGeometry(0.2, 0.22, 1.2, 6),
        new THREE.MeshStandardMaterial({ color: 0x3d7a3d, roughness: 0.85 })
      ));
      arm.position.set(0.45, 1.6, 0);
      arm.rotation.z = -Math.PI / 3;
      cactus.add(arm);
    }
    cactus.position.set(Math.sin(angle) * dist, 0, Math.cos(angle) * dist);
    group.add(cactus);
  }

  // Dead trees / shrubs
  for (let i = 0; i < 8; i++) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 26 + Math.random() * 10;
    const dead = addShadow(new THREE.Mesh(
      new THREE.CylinderGeometry(0.05, 0.15, 2.5, 4),
      new THREE.MeshStandardMaterial({ color: 0x6b5a40, roughness: 0.95 })
    ));
    dead.position.set(Math.sin(angle) * dist, 1.25, Math.cos(angle) * dist);
    dead.rotation.z = (Math.random() - 0.5) * 0.4;
    group.add(dead);
  }
}

export const ENVIRONMENTS = {
  city: {
    label: "CITY",
    description: "Urban ruins — concrete arena surrounded by a neon-lit skyline.",
    sky: 0x1a2233,
    fog: { color: 0x1a2233, near: 22, far: 70 },
    lights: {
      ambient: { color: 0x445566, intensity: 0.55 },
      sun: { color: 0xffeedd, intensity: 1.0, pos: [15, 25, 10] },
      rim1: { color: 0x4488ff, intensity: 0.7, pos: [-10, 8, -10] },
      rim2: { color: 0xff6644, intensity: 0.5, pos: [10, 8, 10] },
    },
    floor: { color: 0x2a2a38, roughness: 0.85, metalness: 0.2, grid: true, gridPrimary: 0x334466, gridSecondary: 0x222233 },
    walls: { color: 0x3a3a48, trimColor: 0x00aaff },
    pillars: { color: 0x4a4a58, style: "box", metalness: 0.4 },
    buildSurroundings: buildCityscape,
  },
  jungle: {
    label: "JUNGLE",
    description: "Dense tropical canopy — fight among palms and ancient trees.",
    sky: 0x1a3320,
    fog: { color: 0x2a5530, near: 18, far: 55 },
    lights: {
      ambient: { color: 0x3a6640, intensity: 0.65 },
      sun: { color: 0xfff0cc, intensity: 0.9, pos: [8, 30, 5] },
      rim1: { color: 0x44aa55, intensity: 0.4, pos: [-12, 6, -8] },
      rim2: { color: 0x88cc44, intensity: 0.35, pos: [12, 5, 12] },
    },
    floor: { color: 0x2a4a20, roughness: 0.95, metalness: 0.0, grid: false },
    walls: { color: 0x3d5a30, trimColor: 0x55aa44 },
    pillars: { color: 0x2a7a2a, style: "palm" },
    buildSurroundings: buildJungle,
  },
  mountains: {
    label: "MOUNTAINS",
    description: "Alpine outpost — rocky cover beneath snow-capped peaks.",
    sky: 0x6a8ab0,
    fog: { color: 0x8aa8c8, near: 25, far: 80 },
    lights: {
      ambient: { color: 0x8899aa, intensity: 0.7 },
      sun: { color: 0xffffee, intensity: 1.15, pos: [20, 35, 8] },
      rim1: { color: 0xaaccff, intensity: 0.35, pos: [-15, 10, -12] },
      rim2: { color: 0xffffff, intensity: 0.2, pos: [8, 12, 15] },
    },
    floor: { color: 0x5a6a50, roughness: 0.92, metalness: 0.0, grid: false },
    walls: { color: 0x6a7068, trimColor: null },
    pillars: { color: 0x5a6068, style: "rock" },
    buildSurroundings: buildMountains,
  },
  desert: {
    label: "DESERT",
    description: "Sun-scorched dunes — open sand arena with cacti and wasteland.",
    sky: 0xe8b878,
    fog: { color: 0xd4a860, near: 30, far: 90 },
    lights: {
      ambient: { color: 0xccaa77, intensity: 0.75 },
      sun: { color: 0xffffcc, intensity: 1.3, pos: [12, 40, 6] },
      rim1: { color: 0xffaa55, intensity: 0.45, pos: [-10, 6, 10] },
      rim2: { color: 0xff8844, intensity: 0.3, pos: [14, 5, -8] },
    },
    floor: { color: 0xc9a86a, roughness: 0.98, metalness: 0.0, grid: false },
    walls: { color: 0xb89060, trimColor: null },
    pillars: { color: 0xa07848, style: "crate" },
    buildSurroundings: buildDesert,
  },
};

export function buildWorld(envId, arenaGroup, surroundingsGroup) {
  const env = ENVIRONMENTS[envId] ?? ENVIRONMENTS.city;
  disposeGroup(arenaGroup);
  disposeGroup(surroundingsGroup);
  buildArenaCore(arenaGroup, env);
  env.buildSurroundings(surroundingsGroup);
  return env;
}

export function applyEnvironmentLighting(scene, env, lights) {
  scene.background = new THREE.Color(env.sky);
  scene.fog = new THREE.Fog(env.fog.color, env.fog.near, env.fog.far);

  lights.ambient.color.setHex(env.lights.ambient.color);
  lights.ambient.intensity = env.lights.ambient.intensity;

  lights.sun.color.setHex(env.lights.sun.color);
  lights.sun.intensity = env.lights.sun.intensity;
  lights.sun.position.set(...env.lights.sun.pos);

  lights.rim1.color.setHex(env.lights.rim1.color);
  lights.rim1.intensity = env.lights.rim1.intensity;
  lights.rim1.position.set(...env.lights.rim1.pos);

  lights.rim2.color.setHex(env.lights.rim2.color);
  lights.rim2.intensity = env.lights.rim2.intensity;
  lights.rim2.position.set(...env.lights.rim2.pos);
}
