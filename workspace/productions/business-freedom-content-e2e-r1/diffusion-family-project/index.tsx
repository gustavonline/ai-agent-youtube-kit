/* @jsxImportSource @diffusionstudio/jsx */

// ACS-owned vertical adaptations and post visual for the reviewed Business
// Freedom family. Native shapes/text only: no media, HTML paint, WebGPU,
// shaders, cloud AI, credits, external URLs, or runtime design dependency.

const W = 1080;
const H = 1920;
const BEAT = 4;
const CREAM = "#F8F2E8";
const PAPER = "#FFFDF7";
const WALNUT = "#2B1B12";
const MUTED = "#766252";
const BORDER = "#DECDB8";
const ORANGE = "#F36F2B";
const TERRACOTTA = "#B86F36";
const SAND = "#F3EAD7";
const GREEN = "#146E59";
const TECH = "#0E1720";
const TECH_SURFACE = "#152534";
const CYAN = "#72D9ED";

type FrameProps = {
  label: string;
  step: number;
  accent?: string;
  fill?: string;
  dark?: boolean;
};

function Frame(props: FrameProps) {
  const foreground = props.dark ? PAPER : WALNUT;
  const secondary = props.dark ? "#A9CDD8" : MUTED;
  return <group name={props.label} id="frme01">
    <rect x={0} y={0} width={W} height={H} fill={props.fill ?? CREAM} end={BEAT} id="frbg01" />
    <rect x={0} y={0} width={18} height={H} fill={props.accent ?? TERRACOTTA} end={BEAT} id="frrail" />
    <text x={76} y={68} width={820} height={38} color={secondary} fontFamily="Inter" fontSize={24} fontWeight={760} letterSpacing={2} end={BEAT} id="frlbl1">
      {props.label}
    </text>
    <text x={924} y={68} width={90} height={38} textAlign="right" color={foreground} fontFamily="Inter" fontSize={24} fontWeight={800} end={BEAT} id="frstp1">
      {props.step}/6
    </text>
    <rect x={76} y={128} width={928} height={5} cornerRadius={3} fill={props.dark ? "#294555" : BORDER} end={BEAT} id="frbar1" />
    <rect x={76} y={128} width={(928 * props.step) / 6} height={5} cornerRadius={3} fill={props.accent ?? TERRACOTTA} end={BEAT} id="frbar2">
      <keyframeTrack property="width" id="frtrk1">
        <keyframe time={0} value={0} id="frkey1" />
        <keyframe time={0.65} value={(928 * props.step) / 6} easing="easeOut" id="frkey2" />
      </keyframeTrack>
    </rect>
  </group>;
}

type HeadlineProps = { children: string; x?: number; y?: number; width?: number; size?: number; color?: string; height?: number };
function Headline(props: HeadlineProps) {
  const y = props.y ?? 220;
  return <text x={props.x ?? 76} y={y} width={props.width ?? 928} height={props.height ?? 300} color={props.color ?? WALNUT} fontFamily="Inter" fontSize={props.size ?? 92} fontWeight={840} letterSpacing={-3} leading={0.98} end={BEAT} id="head01">
    {props.children}
    <keyframeTrack property="opacity" id="headtr">
      <keyframe time={0} value={0} id="headk1" />
      <keyframe time={0.4} value={1} easing="easeOut" id="headk2" />
    </keyframeTrack>
    <keyframeTrack property="y" id="headty">
      <keyframe time={0} value={y + 34} id="headk3" />
      <keyframe time={0.58} value={y} easing="easeOut" id="headk4" />
    </keyframeTrack>
  </text>;
}

function Caption(props: { children: string; dark?: boolean }) {
  return <group name="Open caption" id="capgrp">
    <rect x={76} y={1565} width={928} height={275} cornerRadius={28} fill={props.dark ? PAPER : WALNUT} end={BEAT} id="capbg1" />
    <rect x={76} y={1565} width={16} height={275} cornerRadius={8} fill={TERRACOTTA} end={BEAT} id="capbar" />
    <text x={126} y={1620} width={828} height={170} color={props.dark ? WALNUT : PAPER} fontFamily="Inter" fontSize={43} fontWeight={620} leading={1.18} end={BEAT} id="captxt">
      {props.children}
    </text>
  </group>;
}

function DecisionSlip(props: { y: number; label: string; delay: number }) {
  return <group x={76} y={props.y} id="slpgrp">
    <rect x={0} y={0} width={928} height={150} cornerRadius={22} fill={PAPER} end={BEAT} id="slpbg1">
      <stroke color={BORDER} width={2} id="slpstr" />
      <keyframeTrack property="opacity" id="slptr1">
        <keyframe time={0} value={0} id="slpk01" />
        <keyframe time={props.delay} value={1} easing="easeOut" id="slpk02" />
      </keyframeTrack>
      <keyframeTrack property="x" id="slptr2">
        <keyframe time={0} value={70} id="slpk03" />
        <keyframe time={props.delay + 0.25} value={0} easing="easeOut" id="slpk04" />
      </keyframeTrack>
    </rect>
    <rect x={32} y={50} width={46} height={46} cornerRadius={23} fill={TERRACOTTA} end={BEAT} id="slpdot" />
    <text x={112} y={45} width={760} height={56} color={WALNUT} fontFamily="Inter" fontSize={38} fontWeight={780} letterSpacing={1} end={BEAT} id="slptxt">
      {props.label}
    </text>
  </group>;
}

function ShortOne() {
  return <scene id="business-freedom-short-founder-constraint" name="Short 01 · The content bottleneck is not ideas" width={W} height={H} fill={CREAM} workarea={[0, BEAT * 6]} active>
    <sequence id="short-one-sequence" name="Founder constraint to reviewed handoff">
      <group name="1 · Hook" start={0} end={BEAT} id="s1beat1">
        <Frame label="GUSTAV ONLINE / DEMAND" step={1} accent={ORANGE} />
        <rect x={18} y={160} width={420} height={1285} fill={ORANGE} end={BEAT} id="s1orang" />
        <rect x={112} y={310} width={210} height={210} cornerRadius={105} fill={PAPER} end={BEAT} id="s1head" />
        <rect x={72} y={530} width={290} height={390} cornerRadius={70} fill={WALNUT} end={BEAT} id="s1body" />
        <rect x={205} y={780} width={270} height={180} cornerRadius={22} fill={PAPER} rotation={-3} end={BEAT} id="s1note" />
        <Headline x={490} y={250} width={514} height={420} size={72}>THE CONTENT BOTTLENECK ISN’T IDEAS.</Headline>
        <text x={500} y={750} width={470} height={220} color={MUTED} fontFamily="Inter" fontSize={46} fontWeight={620} leading={1.15} end={BEAT} id="s1sub1">
          Useful knowledge and real cases already exist.
        </text>
        <Caption>Gustav Online can make useful knowledge public learning. The ideas are already there.</Caption>
      </group>

      <group name="2 · Founder queue" start={BEAT} end={BEAT * 2} id="s1beat2">
        <Frame label="FOUNDER CONSTRAINT" step={2} />
        <Headline size={88}>FOUR DECISIONS STILL WAIT FOR GUSTAV.</Headline>
        <DecisionSlip y={600} label="VISUAL CHOICE" delay={0.45} />
        <DecisionSlip y={775} label="PRODUCTION VERSION" delay={0.72} />
        <DecisionSlip y={950} label="LINEAGE" delay={0.99} />
        <DecisionSlip y={1125} label="APPROVAL" delay={1.26} />
        <Caption>Visual choices, production versions, lineage, and approval still depend on one founder.</Caption>
      </group>

      <group name="3 · Diagnose Demand" start={BEAT * 2} end={BEAT * 3} id="s1beat3">
        <Frame label="ONLINESOURDOUGH / DIAGNOSIS" step={3} />
        <Headline size={86}>FIND THE CURRENT CONSTRAINT.</Headline>
        {[
          { label: "OFFER", y: 630, selected: false },
          { label: "OPERATIONS", y: 820, selected: false },
          { label: "DEMAND ✓", y: 1010, selected: true },
        ].map((item) => <group x={76} y={item.y} id="s1diag">
          <rect x={0} y={0} width={928} height={160} cornerRadius={22} fill={item.selected ? WALNUT : PAPER} end={BEAT} id="s1dgbg">
            <stroke color={item.selected ? ORANGE : BORDER} width={item.selected ? 5 : 2} id="s1dgst" />
          </rect>
          <text x={42} y={48} width={820} height={60} color={item.selected ? PAPER : WALNUT} fontFamily="Inter" fontSize={42} fontWeight={820} end={BEAT} id="s1dgtx">{item.label}</text>
        </group>)}
        <Caption>onlinesourdough diagnoses Offer, Operations, and Demand. Here, Demand is the constraint.</Caption>
      </group>

      <group name="4 · AIOS route" start={BEAT * 3} end={BEAT * 4} id="s1beat4">
        <Frame label="AIOS / BOUNDED ROUTE" step={4} fill={TECH} accent={CYAN} dark />
        <Headline size={86} color={PAPER}>CONTEXT. OWNER. ACTION. EVIDENCE.</Headline>
        {[
          ["CONTEXT", "Demand constraint"],
          ["OWNER", "Explicit at each boundary"],
          ["NEXT ACTION", "One bounded change"],
          ["EVIDENCE", "Review + exact bytes"],
        ].map((row, index) => <group x={76} y={620 + index * 185} id="s1rowg">
          <rect x={0} y={0} width={928} height={155} cornerRadius={20} fill={TECH_SURFACE} end={BEAT} id="s1rowb"><stroke color="#285268" width={2} id="s1rows" /></rect>
          <text x={34} y={32} width={280} height={42} color={CYAN} fontFamily="Inter" fontSize={26} fontWeight={820} letterSpacing={1.5} end={BEAT} id="s1rowl">{row[0]}</text>
          <text x={34} y={84} width={840} height={48} color={PAPER} fontFamily="Inter" fontSize={34} fontWeight={620} end={BEAT} id="s1rowv">{row[1]}</text>
        </group>)}
        <Caption dark>AIOS routes bounded context, owner, next action, and evidence. It does not merge the products.</Caption>
      </group>

      <group name="5 · Reviewed production" start={BEAT * 4} end={BEAT * 5} id="s1beat5">
        <Frame label="SEPARATE OWNERSHIP" step={5} />
        <Headline size={84}>ONE REVIEWABLE HANDOFF. THREE OWNERS.</Headline>
        {[
          ["ADS", "Accepted direction", TERRACOTTA],
          ["ACS", "Lineage + review", WALNUT],
          ["DIFFUSION", "Local render", GREEN],
        ].map((card, index) => <group x={76} y={650 + index * 245} id="s1owng">
          <rect x={0} y={0} width={928} height={210} cornerRadius={26} fill={card[2]} end={BEAT} id="s1ownb" />
          <text x={42} y={38} width={840} height={58} color={PAPER} fontFamily="Inter" fontSize={42} fontWeight={840} end={BEAT} id="s1ownl">{card[0]}</text>
          <text x={42} y={112} width={840} height={50} color={PAPER} opacity={0.88} fontFamily="Inter" fontSize={34} fontWeight={600} end={BEAT} id="s1ownv">{card[1]}</text>
        </group>)}
        <Caption>ADS sets direction. ACS holds lineage and review. Diffusion renders locally. Each stays separate.</Caption>
      </group>

      <group name="6 · Business Freedom" start={BEAT * 5} end={BEAT * 6} id="s1beat6">
        <Frame label="BUSINESS FREEDOM / HUMAN CHOICE" step={6} />
        <rect x={76} y={310} width={928} height={950} cornerRadius={40} fill={PAPER} end={BEAT} id="s1close">
          <stroke color={BORDER} width={3} id="s1clst" />
          <keyframeTrack property="scale" id="s1cltr"><keyframe time={0} value={0.92} id="s1clk1" /><keyframe time={0.75} value={1} easing="easeOut" id="s1clk2" /></keyframeTrack>
        </rect>
        <text x={130} y={390} width={820} height={70} textAlign="center" color={TERRACOTTA} fontFamily="Inter" fontSize={28} fontWeight={820} letterSpacing={2} end={BEAT} id="s1clsm">FEWER REPEATED FOUNDER DECISIONS</text>
        <text x={124} y={565} width={832} height={270} textAlign="center" color={WALNUT} fontFamily="Inter" fontSize={104} fontWeight={860} leading={0.94} letterSpacing={-4} end={BEAT} id="s1clhd">BUSINESS FREEDOM</text>
        <text x={150} y={900} width={780} height={170} textAlign="center" color={MUTED} fontFamily="Inter" fontSize={47} fontWeight={620} leading={1.18} end={BEAT} id="s1clcp">Demand keeps moving. Gustav keeps the final choice.</text>
        <rect x={210} y={1110} width={660} height={84} cornerRadius={42} fill={SAND} end={BEAT} id="s1clpl" />
        <text x={250} y={1135} width={580} height={42} textAlign="center" color={GREEN} fontFamily="Inter" fontSize={25} fontWeight={820} letterSpacing={1} end={BEAT} id="s1clpt">SUPERVISED · NOT POSTED</text>
        <Caption>The goal is fewer repeated founder decisions—not hands-off automation. Gustav keeps final approval.</Caption>
      </group>
    </sequence>
  </scene>;
}

function OfferMode(props: { label: string; mode: string; copy: string; color: string; mark: string }) {
  return <group x={76} y={560} id="offgrp">
    <rect x={0} y={0} width={928} height={760} cornerRadius={38} fill={PAPER} end={BEAT} id="offbg1"><stroke color={props.color} width={5} id="offstr" /></rect>
    <rect x={70} y={70} width={170} height={170} cornerRadius={34} fill={props.color} end={BEAT} id="offico" />
    <text x={70} y={95} width={170} height={110} textAlign="center" color={PAPER} fontFamily="Inter" fontSize={72} fontWeight={860} end={BEAT} id="offmrk">{props.mark}</text>
    <text x={290} y={76} width={560} height={90} color={WALNUT} fontFamily="Inter" fontSize={62} fontWeight={840} end={BEAT} id="offlab">{props.label}</text>
    <text x={290} y={176} width={560} height={60} color={props.color} fontFamily="Inter" fontSize={32} fontWeight={820} letterSpacing={1.6} end={BEAT} id="offmod">{props.mode}</text>
    <rect x={70} y={315} width={788} height={4} fill={BORDER} end={BEAT} id="offdiv" />
    <text x={70} y={390} width={788} height={235} color={MUTED} fontFamily="Inter" fontSize={54} fontWeight={620} leading={1.2} end={BEAT} id="offcpy">{props.copy}</text>
  </group>;
}

function ShortTwo() {
  return <scene id="business-freedom-short-offer-choice" name="Short 02 · Who should do the change" width={W} height={H} fill={CREAM} workarea={[0, BEAT * 6]}>
    <sequence id="short-two-sequence" name="Offer menu and retained choice">
      <group name="1 · Hook" start={0} end={BEAT} id="s2beat1">
        <Frame label="ONLINESOURDOUGH / OFFER MENU" step={1} />
        <Headline y={250} size={104} height={360}>WHO SHOULD DO THE CHANGE?</Headline>
        <rect x={76} y={780} width={928} height={420} cornerRadius={34} fill={WALNUT} end={BEAT} id="s2hkbg" />
        <text x={130} y={850} width={820} height={110} textAlign="center" color={PAPER} fontFamily="Inter" fontSize={62} fontWeight={830} end={BEAT} id="s2hkt1">DIY · DONE WITH YOU · DONE FOR YOU</text>
        <text x={160} y={1020} width={760} height={110} textAlign="center" color="#E7D9CB" fontFamily="Inter" fontSize={42} fontWeight={580} end={BEAT} id="s2hkt2">Choose the delivery role after the diagnosis.</text>
        <Caption>Business Freedom starts by choosing who should do the change—not by automating everything.</Caption>
      </group>

      <group name="2 · Diagnosis" start={BEAT} end={BEAT * 2} id="s2beat2">
        <Frame label="UNDERSTAND BEFORE BUILD" step={2} />
        <Headline size={86}>DIAGNOSE THE BUSINESS FIRST.</Headline>
        {[
          ["OFFER", "What is promised?"],
          ["OPERATIONS", "What must happen reliably?"],
          ["DEMAND", "Who is ready to act?"],
        ].map((row, index) => <group x={76} y={650 + index * 235} id="s2dgrp">
          <rect x={0} y={0} width={928} height={200} cornerRadius={26} fill={index === 2 ? WALNUT : PAPER} end={BEAT} id="s2dbgx"><stroke color={index === 2 ? ORANGE : BORDER} width={index === 2 ? 5 : 2} id="s2dstr" /></rect>
          <text x={38} y={35} width={850} height={52} color={index === 2 ? ORANGE : TERRACOTTA} fontFamily="Inter" fontSize={32} fontWeight={830} letterSpacing={1.4} end={BEAT} id="s2dlbl">{row[0]}{index === 2 ? " ✓" : ""}</text>
          <text x={38} y={108} width={850} height={48} color={index === 2 ? PAPER : MUTED} fontFamily="Inter" fontSize={36} fontWeight={600} end={BEAT} id="s2dval">{row[1]}</text>
        </group>)}
        <Caption>onlinesourdough diagnoses Offer, Operations, and Demand. This story selects Demand.</Caption>
      </group>

      <group name="3 · Resources" start={BEAT * 2} end={BEAT * 3} id="s2beat3">
        <Frame label="RESOURCES / DELIVERY CHOICE" step={3} accent={TERRACOTTA} />
        <Headline size={90}>USE THE METHOD YOURSELF.</Headline>
        <OfferMode label="Resources" mode="DIY" copy="Templates and guidance for the owner who wants to do the work." color={TERRACOTTA} mark="1" />
        <Caption>Resources is DIY: the method is available, and the owner does the change.</Caption>
      </group>

      <group name="4 · The Fermentary" start={BEAT * 3} end={BEAT * 4} id="s2beat4">
        <Frame label="THE FERMENTARY / DELIVERY CHOICE" step={4} accent={WALNUT} />
        <Headline size={90}>DO THE CHANGE TOGETHER.</Headline>
        <OfferMode label="The Fermentary" mode="DONE WITH YOU" copy="A collaborative route where capability and decisions stay shared." color={WALNUT} mark="2" />
        <Caption>The Fermentary is done with you: the work and decisions are shared.</Caption>
      </group>

      <group name="5 · Complete Bake" start={BEAT * 4} end={BEAT * 5} id="s2beat5">
        <Frame label="COMPLETE BAKE / ARC’IT AI IN PRACTICE" step={5} fill={SAND} accent={GREEN} />
        <Headline size={88} color={GREEN}>HAND OVER A BOUNDED DELIVERY.</Headline>
        <OfferMode label="Complete Bake" mode="DONE FOR YOU" copy="Arc’IT AI in practice: built, documented, handed over. Not a measured result claim." color={GREEN} mark="3" />
        <Caption>Complete Bake is done for you. Arc’IT AI appears only as that bounded delivery in practice.</Caption>
      </group>

      <group name="6 · Choice stays human" start={BEAT * 5} end={BEAT * 6} id="s2beat6">
        <Frame label="BUSINESS FREEDOM / FINAL CHOICE" step={6} />
        <Headline size={88}>THE MENU SUPPORTS A CHOICE. IT ISN’T ONE STACK.</Headline>
        <rect x={76} y={760} width={928} height={430} cornerRadius={34} fill={PAPER} end={BEAT} id="s2clbg"><stroke color={BORDER} width={3} id="s2clst" /></rect>
        <text x={130} y={830} width={820} height={70} textAlign="center" color={TERRACOTTA} fontFamily="Inter" fontSize={32} fontWeight={820} letterSpacing={1.5} end={BEAT} id="s2clsm">DIY · DWY · DFY</text>
        <text x={150} y={955} width={780} height={170} textAlign="center" color={WALNUT} fontFamily="Inter" fontSize={61} fontWeight={830} leading={1.12} end={BEAT} id="s2cltx">Gustav keeps the final delivery and publishing choice.</text>
        <Caption>Business Freedom means fewer repeated decisions while Gustav still chooses the route and approves publishing.</Caption>
      </group>
    </sequence>
  </scene>;
}

function PostVisual() {
  const PH = 1350;
  return <scene id="business-freedom-post-visual" name="Post visual · Business Freedom" width={1080} height={PH} fill={CREAM} workarea={[0, 3]}>
    <group name="Reviewed post visual" start={0} end={3} id="pvgroup">
      <rect x={0} y={0} width={1080} height={PH} fill={CREAM} end={3} id="pvback" />
      <rect x={0} y={0} width={20} height={PH} fill={TERRACOTTA} end={3} id="pvrail" />
      <text x={76} y={68} width={928} height={36} color={TERRACOTTA} fontFamily="Inter" fontSize={24} fontWeight={820} letterSpacing={2} end={3} id="pvlabel">BUSINESS FREEDOM / DEMAND</text>
      <text x={76} y={170} width={928} height={300} color={WALNUT} fontFamily="Inter" fontSize={92} fontWeight={860} leading={0.96} letterSpacing={-3} end={3} id="pvhead">FEWER REPEATED FOUNDER DECISIONS.</text>
      <text x={76} y={505} width={880} height={120} color={MUTED} fontFamily="Inter" fontSize={40} fontWeight={620} leading={1.18} end={3} id="pvsub">A reviewable Demand-content path—with the final choice still human.</text>
      {[
        ["1", "USEFUL KNOWLEDGE", "Gustav Online / public learning", ORANGE],
        ["2", "REVIEWABLE PRODUCTION", "ADS direction · ACS lineage · Diffusion render", WALNUT],
        ["3", "HUMAN CHOICE", "Supervised · not posted", GREEN],
      ].map((row, index) => <group x={76} y={690 + index * 170} id="pvrowg">
        <rect x={0} y={0} width={928} height={140} cornerRadius={22} fill={PAPER} end={3} id="pvrowb"><stroke color={BORDER} width={2} id="pvrows" /></rect>
        <rect x={26} y={26} width={88} height={88} cornerRadius={20} fill={row[3]} end={3} id="pvnumg" />
        <text x={26} y={42} width={88} height={58} textAlign="center" color={PAPER} fontFamily="Inter" fontSize={43} fontWeight={860} end={3} id="pvnumt">{row[0]}</text>
        <text x={148} y={25} width={730} height={45} color={WALNUT} fontFamily="Inter" fontSize={31} fontWeight={830} end={3} id="pvrowl">{row[1]}</text>
        <text x={148} y={80} width={730} height={38} color={MUTED} fontFamily="Inter" fontSize={27} fontWeight={600} end={3} id="pvrowv">{row[2]}</text>
      </group>)}
      <text x={76} y={1255} width={928} height={42} textAlign="center" color={GREEN} fontFamily="Inter" fontSize={26} fontWeight={820} letterSpacing={1.3} end={3} id="pvfoot">GUSTAV KEEPS THE FINAL CHOICE.</text>
    </group>
  </scene>;
}

export default function BusinessFreedomContentFamily() {
  return <stage id="business-freedom-family-stage" background="#E6D7C5" camera={[0.42, 0, 0, 0.42, 620, 30]}>
    <ShortOne />
    <ShortTwo />
    <PostVisual />
  </stage>;
}
