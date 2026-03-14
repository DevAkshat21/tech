"""
Generates the Three.js 3D globe HTML component.
Used on both landing (centered) and explore (left-side) pages.
"""


def get_globe_html(
    width: int = 600,
    height: int = 600,
    pin_lat: float = None,
    pin_lon: float = None,
    pin_label: str = None,
    pin_value: str = None,
    auto_rotate: bool = True,
    show_rings: bool = True,
    bg_transparent: bool = True,
) -> str:
    pin_js = ""
    if pin_lat is not None and pin_lon is not None:
        pin_js = f"""
        // Convert lat/lon to 3D point on sphere
        var pinLat = {pin_lat} * Math.PI / 180;
        var pinLon = {pin_lon} * Math.PI / 180;
        var pinRadius = 2.05;
        var pinX = pinRadius * Math.cos(pinLat) * Math.sin(pinLon);
        var pinY = pinRadius * Math.sin(pinLat);
        var pinZ = pinRadius * Math.cos(pinLat) * Math.cos(pinLon);

        // Glowing dot
        var pinGeo = new THREE.SphereGeometry(0.06, 16, 16);
        var pinMat = new THREE.MeshBasicMaterial({{ color: 0x4ad4e8 }});
        var pinMesh = new THREE.Mesh(pinGeo, pinMat);
        pinMesh.position.set(pinX, pinY, pinZ);
        globe.add(pinMesh);

        // Pulse ring around pin
        var pulseGeo = new THREE.RingGeometry(0.08, 0.12, 32);
        var pulseMat = new THREE.MeshBasicMaterial({{
            color: 0x4ad4e8, transparent: true, opacity: 0.6, side: THREE.DoubleSide
        }});
        var pulseMesh = new THREE.Mesh(pulseGeo, pulseMat);
        pulseMesh.position.set(pinX, pinY, pinZ);
        pulseMesh.lookAt(new THREE.Vector3(0,0,0));
        globe.add(pulseMesh);

        // Tooltip div
        var tooltip = document.getElementById('globe-tooltip');
        tooltip.style.display = 'block';

        function projectPin() {{
            var worldPos = new THREE.Vector3(pinX, pinY, pinZ);
            worldPos.applyMatrix4(globe.matrixWorld);
            worldPos.project(camera);
            var tw = renderer.domElement.clientWidth;
            var th = renderer.domElement.clientHeight;
            var sx = (worldPos.x * 0.5 + 0.5) * tw;
            var sy = (-(worldPos.y) * 0.5 + 0.5) * th;
            tooltip.style.left = (sx + 12) + 'px';
            tooltip.style.top  = (sy - 40) + 'px';
            tooltip.style.opacity = worldPos.z > 0 ? '1' : '0';
        }}
        animateCallbacks.push(projectPin);
        """

    pin_label_text = pin_label or "Selected Location"
    pin_value_text = pin_value or ""

    bg_color = "transparent" if bg_transparent else "#00000f"
    alpha = "true" if bg_transparent else "false"
    # Pre-compute formatted strings to avoid f-string + None formatting issues
    lat_str = f"{pin_lat:.2f}" if pin_lat is not None else ""
    lon_str = f"{pin_lon:.2f}" if pin_lon is not None else ""
    coords_display = f"{lat_str}°N, {lon_str}°E" if lat_str else ""

    return f"""<!DOCTYPE html>
<html>
<head>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:{bg_color}; overflow:hidden; width:{width}px; height:{height}px; }}
  canvas {{ display:block; }}
  #globe-tooltip {{
    display: none;
    position: absolute;
    background: rgba(0,15,40,0.92);
    border: 1px solid rgba(74,212,232,0.5);
    border-radius: 6px;
    padding: 8px 12px;
    font-family: 'Trebuchet MS', sans-serif;
    pointer-events: none;
    z-index: 100;
    min-width: 160px;
  }}
  #globe-tooltip .tip-name {{ font-weight:700; font-size:13px; color:#fff; }}
  #globe-tooltip .tip-coords {{ font-size:11px; color:#4ad4e8; margin-top:2px; }}
  #globe-tooltip .tip-val {{ font-size:11px; color:#a78bfa; margin-top:2px; }}
</style>
</head>
<body>
<div id="globe-tooltip">
  <div class="tip-name">{pin_label_text}</div>
  <div class="tip-coords">{coords_display}</div>
  <div class="tip-val">{pin_value_text}</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
var animateCallbacks = [];

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(42, {width}/{height}, 0.1, 2000);
camera.position.z = 5.5;

var renderer = new THREE.WebGLRenderer({{ antialias:true, alpha:{alpha} }});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize({width}, {height});
document.body.appendChild(renderer.domElement);

// ── Stars ──────────────────────────────────────────────────────────────────
var starGeo = new THREE.BufferGeometry();
var starPos = [];
for (var i=0; i<6000; i++) {{
    starPos.push(
        (Math.random()-0.5)*1200,
        (Math.random()-0.5)*1200,
        (Math.random()-0.5)*1200
    );
}}
starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
scene.add(new THREE.Points(starGeo,
    new THREE.PointsMaterial({{ color:0xffffff, size:0.6, transparent:true, opacity:0.85 }})));

// ── Globe body ─────────────────────────────────────────────────────────────
var globe = new THREE.Group();
scene.add(globe);

var earthGeo = new THREE.SphereGeometry(2, 64, 64);
var earthMat = new THREE.MeshPhongMaterial({{
    color: 0x0a2a50,
    emissive: 0x041020,
    specular: 0x2288cc,
    shininess: 80,
}});
var earth = new THREE.Mesh(earthGeo, earthMat);
globe.add(earth);

// Continents procedural overlay
var contGeo = new THREE.SphereGeometry(2.005, 64, 64);
var contMat = new THREE.MeshPhongMaterial({{
    color: 0x1a5a30,
    emissive: 0x0a2a15,
    transparent: true,
    opacity: 0.55,
    wireframe: false,
}});
globe.add(new THREE.Mesh(contGeo, contMat));

// ── Atmosphere glow ────────────────────────────────────────────────────────
var atmGeo = new THREE.SphereGeometry(2.25, 64, 64);
var atmMat = new THREE.MeshPhongMaterial({{
    color: 0x0055cc,
    transparent: true,
    opacity: 0.12,
    side: THREE.FrontSide,
}});
scene.add(new THREE.Mesh(atmGeo, atmMat));

// Outer glow ring
var outerGeo = new THREE.SphereGeometry(2.45, 64, 64);
scene.add(new THREE.Mesh(outerGeo,
    new THREE.MeshPhongMaterial({{
        color: 0x0033aa,
        transparent: true,
        opacity: 0.05,
        side: THREE.BackSide,
    }})));

// ── Orbital rings ──────────────────────────────────────────────────────────
{'if show_rings:' if show_rings else 'if False:'}
var ring1 = new THREE.Mesh(
    new THREE.TorusGeometry(3.0, 0.006, 16, 300),
    new THREE.MeshBasicMaterial({{ color:0x4ad4e8, transparent:true, opacity:0.5 }}));
ring1.rotation.x = Math.PI / 3;
scene.add(ring1);

var ring2 = new THREE.Mesh(
    new THREE.TorusGeometry(3.5, 0.004, 16, 300),
    new THREE.MeshBasicMaterial({{ color:0x4ad4e8, transparent:true, opacity:0.25 }}));
ring2.rotation.x = Math.PI / 4;
ring2.rotation.y = Math.PI / 5;
scene.add(ring2);

// ── Lights ─────────────────────────────────────────────────────────────────
scene.add(new THREE.AmbientLight(0x223355, 0.8));
var sun = new THREE.DirectionalLight(0x6699ff, 1.8);
sun.position.set(6, 3, 6);
scene.add(sun);
var rim = new THREE.DirectionalLight(0x0033cc, 0.6);
rim.position.set(-6, -3, -6);
scene.add(rim);

// ── Pin ────────────────────────────────────────────────────────────────────
{pin_js}

// ── Animate ────────────────────────────────────────────────────────────────
var clock = new THREE.Clock();
function animate() {{
    requestAnimationFrame(animate);
    var dt = clock.getDelta();
    {"globe.rotation.y += 0.003;" if auto_rotate else ""}
    ring1 && (ring1.rotation.z += 0.0008);
    ring2 && (ring2.rotation.z -= 0.0005);
    for (var i=0; i<animateCallbacks.length; i++) animateCallbacks[i]();
    renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>"""
