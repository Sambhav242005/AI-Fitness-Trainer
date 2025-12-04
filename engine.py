import numpy as np

# --- LOGIC LAYER: GEOMETRY & FORM ---
class PoseMath:
    """Utilities for calculating angles and vectors from 2D coordinates."""
    
    @staticmethod
    def calculate_angle(a, b, c):
        """Calculates angle ABC (in degrees) where B is the pivot."""
        if any(v is None for v in [a, b, c]):
            return 0
        
        # Create vectors BA and BC
        ba = np.array([a[0] - b[0], a[1] - b[1]])
        bc = np.array([c[0] - b[0], c[1] - b[1]])
        
        # Calculate cosine angle using dot product
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0) # Safety clip
        angle = np.degrees(np.arccos(cosine_angle))
        
        return angle

class RepCounter:
    """State Machine for counting reps and monitoring form."""
    
    def __init__(self, exercise_type="Squat"):
        self.exercise_type = exercise_type
        self.count = 0
        self.stage = "down" # "up" or "down"
        self.feedback = "Get Ready"
        self.form_faults = [] # Track issues like "Not deep enough"
        
        # Hysteresis Thresholds
        self.squat_depth_thresh = 0.95  # Hip Y should be > 95% of Knee Y (pixels go down)
        self.stand_thresh = 170  # Leg straighten angle
        # Relaxed Curl Thresholds
        self.curl_up_thresh = 60   # Easier to hit (was 30)
        self.curl_down_thresh = 150 # Allows slight bend (was 160)
        
        self.pushup_up_thresh = 160
        self.pushup_down_thresh = 90
        
        self.last_side = None # Track which arm was last active to prevent jitter

    def process(self, landmarks):
        """
        Input: landmarks (dict of 'x','y' for key parts)
        Returns: (current_count, current_stage, feedback_text, progress)
        """
        if self.exercise_type == "Squat":
            return self._process_squat(landmarks)
        elif self.exercise_type == "Bicep Curl":
            return self._process_curl(landmarks)
        elif self.exercise_type == "Push Up":
            return self._process_pushup(landmarks)
        return 0, "none", "", 0.0

    def _get_primary_arm(self, lm):
        """
        Determines which arm to track based on visibility.
        Returns: ((shoulder, elbow, wrist), side_name) or (None, None)
        """
        # Left Arm: Shoulder(5), Elbow(7), Wrist(9)
        l_shoulder = lm.get(5)
        l_elbow = lm.get(7)
        l_wrist = lm.get(9)
        
        # Right Arm: Shoulder(6), Elbow(8), Wrist(10)
        r_shoulder = lm.get(6)
        r_elbow = lm.get(8)
        r_wrist = lm.get(10)
        
        left_visible = all([l_shoulder, l_elbow, l_wrist])
        right_visible = all([r_shoulder, r_elbow, r_wrist])
        
        if left_visible and right_visible:
            return (l_shoulder, l_elbow, l_wrist), "Left"
        elif left_visible:
            return (l_shoulder, l_elbow, l_wrist), "Left"
        elif right_visible:
            return (r_shoulder, r_elbow, r_wrist), "Right"
        else:
            return None, None

    def _process_squat(self, lm):
        # Keypoints: Hip(11), Knee(13), Ankle(15) (Using Left Side primarily)
        hip = lm.get(11)
        knee = lm.get(13)
        ankle = lm.get(15)
        
        if not all([hip, knee, ankle]):
            return self.count, self.stage, "Body not fully visible", 0.0

        # Calculate Knee Angle (Hip-Knee-Ankle)
        knee_angle = PoseMath.calculate_angle(hip, knee, ankle)
        
        # State Machine
        # Squat Logic: Stage 'down' means STANDING (confusing, but implies ready to go down)
        # We want to detect the transition from Standing -> Deep Squat -> Standing
        
        # Logic: If angle > 160, we are STANDING (Top)
        if knee_angle > 160:
            self.stage = "up"
            
        # Calculate progress (0.0 to 1.0)
        # 180 deg = 0%, 70 deg = 100% (approx range)
        progress = np.interp(knee_angle, [70, 170], [1.0, 0.0])

        # If angle < 90 (or hip Y is close to knee Y), we are at BOTTOM
        # Note: In pixels, Y increases downwards. Hip Y > Knee Y means Hip is LOWER than Knee.
        # FIX: Use self.squat_depth_thresh (e.g. 0.95)
        if hip[1] >= (knee[1] * self.squat_depth_thresh) and self.stage == "up":
            self.stage = "down"
            self.count += 1
            self.feedback = "Good Depth!"
            
        # Form Correction: Half-repping
        elif knee_angle < 140 and hip[1] < (knee[1] * self.squat_depth_thresh) and self.stage == "up":
             self.feedback = "Go Deeper!"
             
        return self.count, self.stage, self.feedback, progress

    def _process_curl(self, lm):
        # Get coordinates for both arms
        # Left: 5, 7, 9
        l_sh = lm.get(5)
        l_el = lm.get(7)
        l_wr = lm.get(9)
        l_visible = all([l_sh, l_el, l_wr])
        
        # Right: 6, 8, 10
        r_sh = lm.get(6)
        r_el = lm.get(8)
        r_wr = lm.get(10)
        r_visible = all([r_sh, r_el, r_wr])
        
        active_side = None
        points = None
        angle = 180
        
        # Logic to pick the "Active" arm
        if l_visible and r_visible:
            # Both visible: Compare angles
            angle_l = PoseMath.calculate_angle(l_sh, l_el, l_wr)
            angle_r = PoseMath.calculate_angle(r_sh, r_el, r_wr)
            
            # Heuristic: The arm that is curling (smaller angle) is likely the active one.
            # We add a small bias to the last_side to prevent flickering when angles are similar.
            bias = 20
            
            if self.last_side == "Right":
                if angle_l < angle_r - bias: # Left must be significantly more curled to switch
                    active_side = "Left"
                    points = (l_sh, l_el, l_wr)
                    angle = angle_l
                else:
                    active_side = "Right"
                    points = (r_sh, r_el, r_wr)
                    angle = angle_r
            else: # Default or Last was Left
                if angle_r < angle_l - bias: # Right must be significantly more curled to switch
                    active_side = "Right"
                    points = (r_sh, r_el, r_wr)
                    angle = angle_r
                else:
                    active_side = "Left"
                    points = (l_sh, l_el, l_wr)
                    angle = angle_l
                    
        elif l_visible:
            active_side = "Left"
            points = (l_sh, l_el, l_wr)
            angle = PoseMath.calculate_angle(l_sh, l_el, l_wr)
        elif r_visible:
            active_side = "Right"
            points = (r_sh, r_el, r_wr)
            angle = PoseMath.calculate_angle(r_sh, r_el, r_wr)
        else:
            return self.count, self.stage, "Arm not visible", 0.0

        # Update history
        self.last_side = active_side
        
        # --- Standard Curl Logic ---
        
        # Progress: 150 deg = 0%, 50 deg = 100%
        progress = np.interp(angle, [self.curl_up_thresh, self.curl_down_thresh], [1.0, 0.0])
        
        # State Machine
        # Down state: Arm extended (> 150)
        if angle > self.curl_down_thresh:
            self.stage = "down"
            self.feedback = f"{active_side}: Curl Up!"
            
        # Up state: Arm curled (< 50)
        if angle < self.curl_up_thresh and self.stage == "down":
            self.stage = "up"
            self.count += 1
            self.feedback = f"{active_side}: Good Curl!"
            
        # Form feedback during movement
        if self.stage == "down":
            if angle < 100 and angle > self.curl_up_thresh:
                self.feedback = f"{active_side}: Keep Going!"
            else:
                self.feedback = f"{active_side}: Curl Up!"
        elif self.stage == "up":
            if angle < self.curl_down_thresh:
                self.feedback = f"{active_side}: Extend Arm!"
            
        return self.count, self.stage, self.feedback, progress

    def _process_pushup(self, lm):
        # Pushups are similar to curls (Shoulder-Elbow-Wrist) but reversed states.
        # UP = Arms extended (Angle > 160)
        # DOWN = Arms bent (Angle < 90)
        
        shoulder = lm.get(5)
        elbow = lm.get(7)
        wrist = lm.get(9)

        if not all([shoulder, elbow, wrist]):
            return self.count, self.stage, "Arm not visible", 0.0

        angle = PoseMath.calculate_angle(shoulder, elbow, wrist)

        # Logic: Start at UP (180 deg). Go DOWN (< 90 deg). Return UP (> 160 deg)
        
        # Progress: 170 deg = 0%, 80 deg = 100%
        progress = np.interp(angle, [80, 170], [1.0, 0.0])
        
        if angle > self.pushup_up_thresh:
            if self.stage == "down":
                self.count += 1
                self.feedback = "Good Push!"
            self.stage = "up"
            
        if angle < self.pushup_down_thresh:
            self.stage = "down"
            self.feedback = "Deep Enough"

        return self.count, self.stage, f"Angle: {int(angle)}", progress
