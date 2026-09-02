/* @jsxImportSource @diffusionstudio/jsx */

// ACS-owned implementation of the accepted ADS r1 direction. The three
// immutable keyframes in ../design-input guide opener, method, and handoff
// composition; this runtime deliberately loads no media or external assets.

const W = 1920;
const H = 1080;
const BEAT = 5.25;
const CREAM = "#F8F2E8";
const PAPER = "#FFFDF7";
const WALNUT = "#2B1B12";
const MUTED = "#766252";
const BORDER = "#DECDB8";
const ORANGE = "#F36F2B";
const TERRACOTTA = "#B86F36";
const SAND = "#F3EAD7";
const GREEN = "#146E59";
const SUCCESS = "#3B6F55";
const TECHNICAL = "#0E1720";
const TECHNICAL_SURFACE = "#152534";
const CYAN = "#72D9ED";
type BaseProps = {
  prefix: string;
  index: string;
  label: string;
  active: number;
  fill?: string;
  accent?: string;
  dark?: boolean;
};
function BaseFrame(props: BaseProps) {
  const fill = props.fill ?? CREAM;
  const foreground = props.dark ? PAPER : WALNUT;
  const muted = props.dark ? "#A9CDD8" : MUTED;
  const rail = props.dark ? "#294555" : BORDER;
  return <group name={`${props.index} ${props.label}`} id="fx4zw1">
      <rect x={0} y={0} width={W} height={H} fill={fill} end={BEAT} id="eckk2u" />
      <rect x={0} y={0} width={18} height={H} fill={props.accent ?? TERRACOTTA} end={BEAT} id="wlh9aa" />
      <text x={104} y={62} width={86} height={34} color={muted} fontFamily="Inter" fontSize={22} fontWeight={700} letterSpacing={2.5} end={BEAT} id="m42232">
        {props.index}
      </text>
      <text x={210} y={62} width={1100} height={34} color={foreground} fontFamily="Inter" fontSize={22} fontWeight={720} letterSpacing={2.2} end={BEAT} id="xogf11">
        {props.label}
      </text>
      <rect x={104} y={830} width={1712} height={3} fill={rail} end={BEAT} id="ihkjlg" />
      {[0, 1, 2, 3, 4, 5, 6, 7].map(dot => <rect x={104 + dot * 244.5} y={dot === props.active ? 820 : 823} width={dot === props.active ? 22 : 16} height={dot === props.active ? 22 : 16} cornerRadius={dot === props.active ? 11 : 8} fill={dot <= props.active ? props.accent ?? TERRACOTTA : rail} end={BEAT} id="xofg04" />)}
    </group>;
}
type HeadlineProps = {
  prefix: string;
  children: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  color?: string;
  size?: number;
  align?: "left" | "center" | "right";
};
function Headline(props: HeadlineProps) {
  const y = props.y ?? 150;
  return <text x={props.x ?? 104} y={y} width={props.width ?? 1712} height={props.height ?? 190} color={props.color ?? WALNUT} fontFamily="Inter" fontSize={props.size ?? 86} fontWeight={820} letterSpacing={-3.2} leading={0.98} textAlign={props.align ?? "left"} end={BEAT} id="7vy7cv">
      {props.children}
      <keyframeTrack property="opacity" id="326ckn">
        <keyframe time={0} value={0} id="um7rke" />
        <keyframe time={0.42} value={1} easing="easeOut" id="k9zlw2" />
      </keyframeTrack>
      <keyframeTrack property="y" id="8x8vnd">
        <keyframe time={0} value={y + 28} id="rofhcj" />
        <keyframe time={0.58} value={y} easing="easeOut" id="hyfke0" />
      </keyframeTrack>
    </text>;
}
function Caption(props: {
  prefix: string;
  children: string;
  dark?: boolean;
}) {
  return <group name="Open caption" id="33kdz1">
      <rect x={104} y={875} width={1712} height={142} cornerRadius={18} fill={props.dark ? PAPER : WALNUT} end={BEAT} id="6uok3p" />
      <rect x={104} y={875} width={16} height={142} cornerRadius={8} fill={TERRACOTTA} end={BEAT} id="7defjh" />
      <text x={150} y={904} width={1618} height={90} color={props.dark ? WALNUT : PAPER} fontFamily="Inter" fontSize={34} fontWeight={600} leading={1.15} end={BEAT} id="dkxpqn">
        {props.children}
      </text>
    </group>;
}
function FounderSource() {
  const prefix = "founder-source";
  return <group name="1 · Gustav Online public learning" start={0} end={BEAT} id="qfy9et">
      <BaseFrame prefix={prefix} index="00:00" label="GUSTAV ONLINE / DEMAND" active={0} accent={ORANGE} />
      <rect x={18} y={0} width={720} height={830} fill={ORANGE} end={BEAT} id="wmaqet" />
      <rect x={214} y={176} width={170} height={170} cornerRadius={85} fill={PAPER} opacity={0.92} end={BEAT} id="vseatd" />
      <rect x={142} y={352} width={314} height={286} cornerRadius={72} fill={WALNUT} opacity={0.9} end={BEAT} id="8244lv" />
      <rect x={340} y={512} width={252} height={164} cornerRadius={18} fill={PAPER} end={BEAT} id="ch7vwx">
        <stroke color={WALNUT} opacity={0.22} width={2} id="k3bppm" />
        <keyframeTrack property="rotation" id="q0q5qz">
          <keyframe time={0} value={-8} id="d7fyx7" />
          <keyframe time={1.05} value={-3} easing="easeOut" id="xd9o6b" />
        </keyframeTrack>
      </rect>
      <rect x={374} y={552} width={154} height={10} cornerRadius={5} fill={TERRACOTTA} end={BEAT} id="8ztmvq" />
      <rect x={374} y={582} width={112} height={8} cornerRadius={4} fill={BORDER} end={BEAT} id="7m48s0" />
      <text x={104} y={700} width={560} height={60} color={PAPER} fontFamily="Inter" fontSize={26} fontWeight={720} end={BEAT} id="u64mek">
        HUMAN VOICE · PUBLIC LEARNING
      </text>
      <Headline prefix={prefix} x={828} y={188} width={900} height={250} size={94}>
        THE USEFUL IDEA IS HERE.
      </Headline>
      <text x={834} y={470} width={800} height={118} color={MUTED} fontFamily="Inter" fontSize={40} fontWeight={620} leading={1.12} end={BEAT} id="ldqocl">
        Useful material and cases already exist.
      </text>
      <rect x={828} y={665} width={0} height={7} cornerRadius={4} fill={TERRACOTTA} end={BEAT} id="uqig52">
        <keyframeTrack property="width" id="noibj3">
          <keyframe time={0.6} value={0} id="kjt3mu" />
          <keyframe time={2.25} value={900} easing="easeOut" id="pfk9bs" />
        </keyframeTrack>
      </rect>
      <Caption prefix={prefix}>Useful knowledge and real cases already exist. Gustav Online makes them public learning.</Caption>
    </group>;
}
function QueueSlip(props: {
  prefix: string;
  x: number;
  label: string;
  delay: number;
  rotation: number;
}) {
  return <group x={props.x} y={575} id="xy855l">
      <rect x={0} y={0} width={340} height={136} cornerRadius={14} fill={PAPER} rotation={props.rotation} end={BEAT} id="xrckpc">
        <stroke color={BORDER} width={2} id="1flvg8" />
        <keyframeTrack property="opacity" id="9nobfv">
          <keyframe time={0} value={0} id="6qgakf" />
          <keyframe time={props.delay} value={1} easing="easeOut" id="fbozfe" />
        </keyframeTrack>
        <keyframeTrack property="y" id="6fpowf">
          <keyframe time={0} value={44} id="e911wh" />
          <keyframe time={props.delay + 0.35} value={0} easing="easeOut" id="4ee30z" />
        </keyframeTrack>
      </rect>
      <text x={24} y={47} width={292} height={42} color={WALNUT} fontFamily="Inter" fontSize={24} fontWeight={760} letterSpacing={1.1} textAlign="center" end={BEAT} id="7g8vay">
        {props.label}
      </text>
    </group>;
}
function FounderQueue() {
  const prefix = "founder-queue";
  return <group name="2 · Founder-owned queue" start={BEAT} end={BEAT * 2} id="wfl0p8">
      <BaseFrame prefix={prefix} index="00:05" label="THE CURRENT CONSTRAINT" active={1} accent={TERRACOTTA} />
      <Headline prefix={prefix} y={150} width={1550} height={220} size={84}>
        THE CONTENT STILL WAITS FOR GUSTAV.
      </Headline>
      <text x={108} y={365} width={1200} height={62} color={MUTED} fontFamily="Inter" fontSize={34} fontWeight={540} end={BEAT} id="0eznpy">
        Four repeated decisions. One founder-owned queue.
      </text>
      <rect x={104} y={643} width={1712} height={7} cornerRadius={4} fill={TERRACOTTA} end={BEAT} id="pnbdlx" />
      <rect x={90} y={628} width={36} height={36} cornerRadius={18} fill={TERRACOTTA} end={BEAT} id="vcm54g" />
      <rect x={1788} y={628} width={36} height={36} cornerRadius={18} fill={WALNUT} end={BEAT} id="gvqyij" />
      <QueueSlip prefix={`${prefix}-visual`} x={170} label="VISUAL CHOICE" delay={0.5} rotation={-2} />
      <QueueSlip prefix={`${prefix}-version`} x={585} label="VERSION" delay={0.78} rotation={2} />
      <QueueSlip prefix={`${prefix}-production`} x={1000} label="PRODUCTION" delay={1.06} rotation={-1} />
      <QueueSlip prefix={`${prefix}-approval`} x={1415} label="APPROVAL" delay={1.34} rotation={2} />
      <Caption prefix={prefix}>But visual choices, versions, production, and approval still wait for Gustav.</Caption>
    </group>;
}
function DiagnoseDemand() {
  const prefix = "diagnose-demand";
  const cards = [{
    slug: "offer",
    label: "OFFER",
    copy: "What is promised?",
    x: 104,
    selected: false
  }, {
    slug: "operations",
    label: "OPERATIONS",
    copy: "What must happen reliably?",
    x: 684,
    selected: false
  }, {
    slug: "demand",
    label: "DEMAND ✓",
    copy: "Who is ready to act?",
    x: 1264,
    selected: true
  }];
  return <group name="3 · Diagnose Demand" start={BEAT * 2} end={BEAT * 3} id="scsaue">
      <BaseFrame prefix={prefix} index="00:10" label="ONLINESOURDOUGH / FIND" active={2} accent={TERRACOTTA} />
      <Headline prefix={prefix} y={145} height={150} size={84}>
        FIND THE CURRENT CONSTRAINT.
      </Headline>
      <text x={108} y={300} width={1540} height={54} color={MUTED} fontFamily="Inter" fontSize={31} fontWeight={540} end={BEAT} id="5y65zn">
        Understand the business before choosing the smallest complete change.
      </text>
      <group name="Offer operations demand" y={410} id="ml2bj2">
        {cards.map((card, i) => <group x={card.x} y={0} id="3ukrvd">
            <rect x={0} y={0} width={500} height={250} cornerRadius={22} fill={card.selected ? WALNUT : PAPER} end={BEAT} id="lypo9y">
              <stroke color={card.selected ? ORANGE : BORDER} width={card.selected ? 5 : 2} id="67jh6v" />
              <keyframeTrack property="opacity" id="xleo04">
                <keyframe time={0} value={0} id="76ey8x" />
                <keyframe time={0.45 + i * 0.22} value={1} easing="easeOut" id="nur93y" />
              </keyframeTrack>
              <keyframeTrack property="y" id="08rff5">
                <keyframe time={0} value={34} id="9s0i26" />
                <keyframe time={0.72 + i * 0.22} value={0} easing="easeOut" id="pzvuef" />
              </keyframeTrack>
            </rect>
            <rect x={34} y={34} width={86} height={9} cornerRadius={5} fill={card.selected ? ORANGE : TERRACOTTA} end={BEAT} id="s1eyw7" />
            <text x={34} y={76} width={432} height={52} color={card.selected ? PAPER : WALNUT} fontFamily="Inter" fontSize={34} fontWeight={800} end={BEAT} id="yiizl7">
              {card.label}
            </text>
            <text x={34} y={146} width={432} height={72} color={card.selected ? "#E7D9CB" : MUTED} fontFamily="Inter" fontSize={28} fontWeight={540} end={BEAT} id="780mro">
              {card.copy}
            </text>
          </group>)}
      </group>
      <Caption prefix={prefix}>Diagnose Offer, Operations, and Demand. Here, Demand is the current constraint.</Caption>
    </group>;
}
function OfferCard(props: {
  prefix: string;
  x: number;
  label: string;
  mode: string;
  copy: string;
  accent: string;
  delay: number;
}) {
  return <group x={props.x} y={430} id="5czxb7">
      <rect x={0} y={0} width={520} height={310} cornerRadius={24} fill={PAPER} end={BEAT} id="28h3zw">
        <stroke color={props.accent} opacity={0.75} width={3} id="k5f1wn" />
        <keyframeTrack property="opacity" id="slbxaf">
          <keyframe time={0} value={0} id="m2b7i8" />
          <keyframe time={props.delay} value={1} easing="easeOut" id="ydqpct" />
        </keyframeTrack>
      </rect>
      <rect x={38} y={48} width={94} height={94} cornerRadius={12} fill={props.accent} opacity={0.16} end={BEAT} id="uho6nu" />
      <rect x={60} y={70} width={94} height={94} cornerRadius={12} fill={props.accent} opacity={0.28} end={BEAT} id="5inhu2" />
      <text x={184} y={50} width={300} height={52} color={WALNUT} fontFamily="Inter" fontSize={34} fontWeight={800} end={BEAT} id="40uyc4">
        {props.label}
      </text>
      <text x={184} y={112} width={300} height={42} color={props.accent} fontFamily="Inter" fontSize={24} fontWeight={800} letterSpacing={1.4} end={BEAT} id="bcx1um">
        {props.mode}
      </text>
      <text x={38} y={210} width={440} height={60} color={MUTED} fontFamily="Inter" fontSize={28} fontWeight={540} end={BEAT} id="0j1di1">
        {props.copy}
      </text>
    </group>;
}
function OfferMenu() {
  const prefix = "offer-menu";
  return <group name="4 · Offer menu" start={BEAT * 3} end={BEAT * 4} id="fibgpj">
      <BaseFrame prefix={prefix} index="00:15" label="ONLINESOURDOUGH / METHOD + OFFER MENU" active={3} accent={TERRACOTTA} />
      <text x={104} y={132} width={500} height={60} color={WALNUT} fontFamily="Inter" fontSize={30} fontWeight={800} letterSpacing={1.5} end={BEAT} id="vue4hd">
        ◼ ONLINESOURDOUGH
      </text>
      <Headline prefix={prefix} y={205} height={145} size={72}>
        CHOOSE WHO SHOULD DO THE CHANGE.
      </Headline>
      <text x={108} y={350} width={1500} height={44} color={MUTED} fontFamily="Inter" fontSize={24} fontWeight={620} end={BEAT} id="b2dsip">
        UNDERSTAND → FIND → CHOOSE → BUILD + PROVE → LAUNCH · OPERATE · RECOVER
      </text>
      <OfferCard prefix={`${prefix}-resources`} x={104} label="Resources" mode="DIY" copy="Do it yourself." accent={TERRACOTTA} delay={0.45} />
      <OfferCard prefix={`${prefix}-fermentary`} x={700} label="The Fermentary" mode="DONE WITH YOU" copy="Work together." accent={WALNUT} delay={0.75} />
      <OfferCard prefix={`${prefix}-complete`} x={1296} label="Complete Bake" mode="DONE FOR YOU" copy="A bounded delivery choice." accent={GREEN} delay={1.05} />
      <Caption prefix={prefix}>Resources is DIY. The Fermentary is done with you. Complete Bake is done for you.</Caption>
    </group>;
}
function PracticeCard(props: {
  prefix: string;
  x: number;
  label: string;
  copy: string;
  delay: number;
}) {
  return <group x={props.x} y={505} id="1hxp72">
      <rect x={0} y={0} width={470} height={190} cornerRadius={20} fill={PAPER} end={BEAT} id="y683mm">
        <stroke color={GREEN} opacity={0.45} width={3} id="pwc47i" />
        <keyframeTrack property="scale" id="p9i7pf">
          <keyframe time={0} value={0.92} id="47b7sq" />
          <keyframe time={props.delay} value={1} easing="easeOut" id="c01r2y" />
        </keyframeTrack>
        <keyframeTrack property="opacity" id="bsv3t1">
          <keyframe time={0} value={0} id="xqbkxp" />
          <keyframe time={props.delay - 0.2} value={1} easing="easeOut" id="36uaqq" />
        </keyframeTrack>
      </rect>
      <rect x={30} y={32} width={30} height={30} cornerRadius={15} fill={GREEN} end={BEAT} id="pcdov0" />
      <text x={82} y={27} width={340} height={48} color={GREEN} fontFamily="Inter" fontSize={30} fontWeight={800} end={BEAT} id="n5z3gy">
        {props.label}
      </text>
      <text x={30} y={100} width={400} height={55} color={MUTED} fontFamily="Inter" fontSize={25} fontWeight={540} end={BEAT} id="jyrsku">
        {props.copy}
      </text>
    </group>;
}
function CompleteBakePractice() {
  const prefix = "complete-bake-practice";
  return <group name="5 · Complete Bake in practice" start={BEAT * 4} end={BEAT * 5} id="g9tjrf">
      <BaseFrame prefix={prefix} index="00:21" label="COMPLETE BAKE / ARC’IT AI · IN PRACTICE" active={4} fill={SAND} accent={GREEN} />
      <rect x={1260} y={92} width={556} height={230} cornerRadius={22} fill={GREEN} end={BEAT} id="xvp913" />
      <text x={1305} y={128} width={450} height={48} color={PAPER} fontFamily="Inter" fontSize={28} fontWeight={800} letterSpacing={2} end={BEAT} id="xo7g49">
        ARC’IT AI / IN PRACTICE
      </text>
      <text x={1305} y={200} width={450} height={70} color={PAPER} fontFamily="Inter" fontSize={46} fontWeight={800} end={BEAT} id="g75m8y">
        COMPLETE BAKE
      </text>
      <Headline prefix={prefix} y={150} width={1050} height={190} size={74} color={GREEN}>
        BUILT. DOCUMENTED. HANDED OVER.
      </Headline>
      <text x={108} y={360} width={1050} height={52} color={MUTED} fontFamily="Inter" fontSize={28} fontWeight={620} end={BEAT} id="mvgg3b">
        Delivery language—not a measured customer result.
      </text>
      <PracticeCard prefix={`${prefix}-built`} x={104} label="BUILT" copy="Bounded implementation" delay={0.75} />
      <PracticeCard prefix={`${prefix}-documented`} x={725} label="DOCUMENTED" copy="Inspectable operating truth" delay={1.05} />
      <PracticeCard prefix={`${prefix}-handover`} x={1346} label="HANDED OVER" copy="Ownership stays explicit" delay={1.35} />
      <Caption prefix={prefix}>Arc’IT AI shows Complete Bake in practice: built, documented, and handed over—not a measured result.</Caption>
    </group>;
}
function ProofRow(props: {
  prefix: string;
  y: number;
  label: string;
  value: string;
  delay: number;
}) {
  return <group x={104} y={props.y} id="gbq5ha">
      <rect x={0} y={0} width={1000} height={90} cornerRadius={14} fill={TECHNICAL_SURFACE} end={BEAT} id="kudmy5">
        <stroke color="#285268" width={2} id="1y1nkf" />
        <keyframeTrack property="opacity" id="brvcul">
          <keyframe time={0} value={0} id="3s0kin" />
          <keyframe time={props.delay} value={1} easing="easeOut" id="ro66hz" />
        </keyframeTrack>
      </rect>
      <text x={30} y={28} width={250} height={36} color={CYAN} fontFamily="Inter" fontSize={24} fontWeight={800} letterSpacing={1.2} end={BEAT} id="utgk0n">
        {props.label}
      </text>
      <text x={330} y={28} width={620} height={36} color={PAPER} fontFamily="Inter" fontSize={25} fontWeight={620} end={BEAT} id="98hrop">
        {props.value}
      </text>
    </group>;
}
function AiosProof() {
  const prefix = "aios-proof";
  return <group name="6 · AIOS bounded proof" start={BEAT * 5} end={BEAT * 6} id="0utzwd">
      <BaseFrame prefix={prefix} index="00:26" label="AIOS / LOCAL ROUTE + EVIDENCE" active={5} fill={TECHNICAL} accent={CYAN} dark />
      <Headline prefix={prefix} y={135} width={1180} height={160} size={74} color={PAPER}>
        CONTEXT. ROUTE. OWNER. EVIDENCE.
      </Headline>
      <ProofRow prefix={`${prefix}-context`} y={320} label="CONTEXT" value="Demand constraint" delay={0.5} />
      <ProofRow prefix={`${prefix}-route`} y={425} label="ROUTE" value="One bounded next action" delay={0.75} />
      <ProofRow prefix={`${prefix}-owner`} y={530} label="OWNER" value="Explicit at every boundary" delay={1.0} />
      <ProofRow prefix={`${prefix}-evidence`} y={635} label="EVIDENCE" value="Review + exact handoff" delay={1.25} />
      <rect x={1190} y={320} width={626} height={405} cornerRadius={22} fill={PAPER} end={BEAT} id="sovkyl" />
      <text x={1234} y={358} width={520} height={40} color={MUTED} fontFamily="Inter" fontSize={22} fontWeight={760} letterSpacing={1.5} end={BEAT} id="amrepy">
        SEPARATELY OWNED
      </text>
      {[{
      slug: "repo",
      label: "REPOSITORY",
      x: 1234,
      y: 430
    }, {
      slug: "project",
      label: "PROJECT",
      x: 1510,
      y: 430
    }, {
      slug: "template",
      label: "TEMPLATE",
      x: 1234,
      y: 550
    }, {
      slug: "skill",
      label: "SKILL",
      x: 1510,
      y: 550
    }].map(item => <group x={item.x} y={item.y} id="1nrdnv">
          <rect x={0} y={0} width={230} height={82} cornerRadius={12} fill={SAND} end={BEAT} id="4lld4g" />
          <text x={18} y={27} width={194} height={30} textAlign="center" color={WALNUT} fontFamily="Inter" fontSize={20} fontWeight={760} end={BEAT} id="xgd5sy">
            {item.label}
          </text>
        </group>)}
      <text x={1234} y={665} width={520} height={34} color={WALNUT} fontFamily="Inter" fontSize={22} fontWeight={720} end={BEAT} id="ctbctl">
        MODULAR · NEVER ONE INSTALLED STACK
      </text>
      <Caption prefix={prefix} dark>AIOS routes context, owner, next action, and evidence. The products remain separately owned.</Caption>
    </group>;
}
function OwnerPanel(props: {
  prefix: string;
  x: number;
  width: number;
  owner: string;
  headline: string;
  copy: string;
  dark?: boolean;
  delay: number;
}) {
  const fill = props.dark ? WALNUT : PAPER;
  const foreground = props.dark ? PAPER : WALNUT;
  const muted = props.dark ? "#E7D9CB" : MUTED;
  return <group x={props.x} y={380} id="qmrnqa">
      <rect x={0} y={0} width={props.width} height={355} cornerRadius={22} fill={fill} end={BEAT} id="s2ci0d">
        <stroke color={props.dark ? WALNUT : BORDER} width={2} id="2gfowi" />
        <keyframeTrack property="opacity" id="lrhy0q">
          <keyframe time={0} value={0} id="zb06wh" />
          <keyframe time={props.delay} value={1} easing="easeOut" id="ki8nqe" />
        </keyframeTrack>
        <keyframeTrack property="y" id="72ngfw">
          <keyframe time={0} value={36} id="l96o0e" />
          <keyframe time={props.delay + 0.28} value={0} easing="easeOut" id="p1ul50" />
        </keyframeTrack>
      </rect>
      <text x={32} y={36} width={props.width - 64} height={40} color={muted} fontFamily="Inter" fontSize={22} fontWeight={760} letterSpacing={1.5} end={BEAT} id="xwc641">
        {props.owner}
      </text>
      <text x={32} y={102} width={props.width - 64} height={70} color={foreground} fontFamily="Inter" fontSize={42} fontWeight={800} end={BEAT} id="lum76u">
        {props.headline}
      </text>
      <text x={32} y={202} width={props.width - 64} height={105} color={muted} fontFamily="Inter" fontSize={25} fontWeight={540} leading={1.18} end={BEAT} id="z3mygh">
        {props.copy}
      </text>
    </group>;
}
function ReviewedProduction() {
  const prefix = "reviewed-production";
  return <group name="7 · Reviewed production" start={BEAT * 6} end={BEAT * 7} id="w5wga7">
      <BaseFrame prefix={prefix} index="00:31" label="ADS → ACS → DIFFUSION / SELECTED HANDOFF" active={6} accent={TERRACOTTA} />
      <Headline prefix={prefix} y={135} height={180} size={76}>
        REUSABLE DIRECTION. REVIEWABLE PRODUCTION.
      </Headline>
      <rect x={104} y={560} width={1712} height={7} cornerRadius={4} fill={TERRACOTTA} end={BEAT} id="mtwe3p">
        <keyframeTrack property="width" id="9yc9ok">
          <keyframe time={0.35} value={0} id="gdl8t0" />
          <keyframe time={2.1} value={1712} easing="easeOut" id="8b65la" />
        </keyframeTrack>
      </rect>
      <OwnerPanel prefix={`${prefix}-ads`} x={104} width={420} owner="ADS / VISUAL OWNER" headline="Direction" copy="Brand roles · hierarchy · selected keyframes" delay={0.55} />
      <OwnerPanel prefix={`${prefix}-acs`} x={610} width={650} owner="ACS / CONTENT OWNER" headline="Lineage + review" copy="Final thesis · versions · independent node approval · supervised handoff" dark delay={0.9} />
      <OwnerPanel prefix={`${prefix}-diffusion`} x={1346} width={470} owner="DIFFUSION STUDIO" headline="Local render" copy="Electron / DAPI authority · code-native project" delay={1.25} />
      <rect x={1530} y={640} width={226} height={72} cornerRadius={10} fill={PAPER} end={BEAT} id="wftmlg">
        <stroke color={MUTED} width={2} id="noedpu" />
      </rect>
      <rect x={1550} y={660} width={14} height={14} cornerRadius={7} fill={CYAN} end={BEAT} id="2bk3v5" />
      <text x={1580} y={654} width={150} height={32} color={WALNUT} fontFamily="Inter" fontSize={18} fontWeight={760} end={BEAT} id="f9yvwa">
        HUMAN REVIEW
      </text>
      <Caption prefix={prefix}>ADS sets direction. ACS holds lineage and independent review. Diffusion renders locally for human inspection.</Caption>
    </group>;
}
function BusinessFreedom() {
  const prefix = "business-freedom";
  return <group name="8 · Business Freedom" start={BEAT * 7} end={BEAT * 8} id="02idkt">
      <BaseFrame prefix={prefix} index="00:36" label="BUSINESS FREEDOM / HUMAN CHOICE" active={7} accent={TERRACOTTA} />
      <rect x={104} y={170} width={520} height={470} cornerRadius={26} fill={WALNUT} end={BEAT} id="rwod4x">
        <keyframeTrack property="x" id="iivdsl">
          <keyframe time={0} value={104} id="vli8gk" />
          <keyframe time={1.1} value={-470} easing="easeOut" id="dj0o3e" />
        </keyframeTrack>
      </rect>
      <rect x={624} y={170} width={520} height={470} cornerRadius={26} fill={WALNUT} end={BEAT} id="sd98gb">
        <keyframeTrack property="x" id="28ytwd">
          <keyframe time={0} value={624} id="8sg823" />
          <keyframe time={1.1} value={1230} easing="easeOut" id="owalhk" />
        </keyframeTrack>
      </rect>
      <rect x={260} y={145} width={1400} height={560} cornerRadius={30} fill={PAPER} end={BEAT} id="hm8grb">
        <stroke color={BORDER} width={2} id="rr7q5f" />
        <keyframeTrack property="opacity" id="civ3p7">
          <keyframe time={0} value={0} id="ejqtxw" />
          <keyframe time={1.0} value={1} easing="easeOut" id="y3qa72" />
        </keyframeTrack>
        <keyframeTrack property="scale" id="wj82ex">
          <keyframe time={0} value={0.92} id="ftew1s" />
          <keyframe time={1.3} value={1} easing="easeOut" id="j10gq9" />
        </keyframeTrack>
      </rect>
      <text x={360} y={210} width={1100} height={54} textAlign="center" color={TERRACOTTA} fontFamily="Inter" fontSize={25} fontWeight={800} letterSpacing={2} end={BEAT} id="jxvzse">
        FEWER REPEATED FOUNDER DECISIONS
      </text>
      <text x={330} y={300} width={1260} height={125} textAlign="center" color={WALNUT} fontFamily="Inter" fontSize={96} fontWeight={850} letterSpacing={-4} end={BEAT} id="qgxrvj">
        BUSINESS FREEDOM
      </text>
      <text x={390} y={455} width={1140} height={76} textAlign="center" color={MUTED} fontFamily="Inter" fontSize={36} fontWeight={600} end={BEAT} id="u273cg">
        Demand keeps moving. Gustav keeps the choice.
      </text>
      <rect x={1430} y={560} width={92} height={92} cornerRadius={46} fill={SUCCESS} end={BEAT} id="fw2nm0" />
      <text x={1430} y={573} width={92} height={62} textAlign="center" color={PAPER} fontFamily="Inter" fontSize={52} fontWeight={850} end={BEAT} id="lxwd3x">
        ✓
      </text>
      <rect x={580} y={570} width={720} height={70} cornerRadius={35} fill={SAND} end={BEAT} id="bicw7r" />
      <text x={610} y={590} width={660} height={32} textAlign="center" color={GREEN} fontFamily="Inter" fontSize={23} fontWeight={800} letterSpacing={1.4} end={BEAT} id="rebf9g">
        SUPERVISED · NOT POSTED · HUMAN APPROVAL
      </text>
      <Caption prefix={prefix}>The handoff stays supervised and unposted. Gustav keeps the final choice: Business Freedom.</Caption>
    </group>;
}
export default function BusinessFreedomContentStory() {
  return <stage id="business-freedom-stage" background="#E6D7C5" camera={[0.33, 0, 0, 0.33, 51.26, 87.97]}>
      <scene id="business-freedom-story" name="Business Freedom · one reviewed Demand constraint" width={W} height={H} fill={CREAM} workarea={[0, BEAT * 8]} active>
        <sequence id="business-freedom-sequence" name="Eight-beat supervised story">
          <FounderSource />
          <FounderQueue />
          <DiagnoseDemand />
          <OfferMenu />
          <CompleteBakePractice />
          <AiosProof />
          <ReviewedProduction />
          <BusinessFreedom />
        </sequence>
      </scene>
    </stage>;
}
