switching_loss_scale= [ 1071 561 331 221 178 153];
switching_speed_scale=[1 2 4 6 8 10];
k=3;
switching_loss=switching_loss_scale(k);

switching_loss_addition= 25; %W per switch

conduction_loss= 9677; % W per die at 100 degree
conduction_loss=conduction_loss/1.2; % at 75 degree


switching_loss_multiplier= 1/10e3;

P_sw=[];
P_con=[];
fsw_tot=5e3:1e3:30e3;
die_num_tot=5:1:25;

for fsw= fsw_tot
P_sw_1=[];
P_con_1=[];

    for die_num=die_num_tot
    P_con_1=[P_con_1, conduction_loss/die_num ];
    P_sw_1=[ P_sw_1 fsw*switching_loss_multiplier*(switching_loss+switching_loss_addition*die_num)];
    end

P_sw=[P_sw ; P_sw_1];
P_con= [P_con ; P_con_1];

end
P_tot= P_sw+P_con;
%%
[X,Y] = meshgrid(die_num_tot,fsw_tot/1e3);
%%
figure1 = figure;
% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');
% Create contour
contour(X,Y,P_tot,'FaceColor','flat');
% Create ylabel
ylabel({'Switching Frequency (kHz)'});
% Create xlabel
xlabel({'Number of Parallel Dies'});
% Create title
title({'Power Loss (W)'});
box(axes1,'on');
axis(axes1,'tight');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'BoxStyle','full','Colormap',...
    [0.058925565098879 0 0;0.0977692361093804 0.0511309992564914 0.0511309992564914;0.125081672664709 0.0723101526062187 0.0723101526062187;0.147417862363388 0.0885614885540095 0.0885614885540095;0.166789170664586 0.102261998512983 0.102261998512983;0.184133725205813 0.114332390095006 0.114332390095006;0.199979574120357 0.12524485821703 0.12524485821703;0.214658872103039 0.135279908318905 0.135279908318905;0.228396656454815 0.144620305212437 0.144620305212437;0.241353752792303 0.153392997769474 0.153392997769474;0.253649828097946 0.161690416690889 0.161690416690889;0.265376782332794 0.169582339689723 0.169582339689723;0.276607009868688 0.177122977108019 0.177122977108019;0.287398746023163 0.184355439584991 0.184355439584991;0.297799665081873 0.191314681061184 0.191314681061184;0.3078493817276 0.198029508595335 0.198029508595335;0.317581238641792 0.204523997025965 0.204523997025965;0.32702361450581 0.210818510677892 0.210818510677892;0.336200900878677 0.216930457818656 0.216930457818656;0.345134244981317 0.222874858641299 0.222874858641299;0.353842123504273 0.228664780190012 0.228664780190012;0.362340792173891 0.234311674451602 0.234311674451602;0.370644642454727 0.239825644728167 0.239825644728167;0.37876648780955 0.24521565805276 0.24521565805276;0.386717795808224 0.25048971643406 0.25048971643406;0.394508878102839 0.255654996282457 0.255654996282457;0.402149047256301 0.260717962958348 0.260717962958348;0.409646747230269 0.265684465662029 0.265684465662029;0.417009662745996 0.270559816637809 0.270559816637809;0.424244811554271 0.275348857749678 0.275348857749678;0.431358622769858 0.280056016805602 0.280056016805602;0.438357003759605 0.284685355496181 0.284685355496181;0.445245397564408 0.289240610424875 0.289240610424875;0.452028832442663 0.293725228409004 0.293725228409004;0.458711964817429 0.298142396999972 0.298142396999972;0.465299116669972 0.30249507099101 0.30249507099101;0.47179430823299 0.306785995538948 0.306785995538948;0.478201286686093 0.311017726414092 0.311017726414092;0.484523551435247 0.315192647802512 0.315192647802512;0.49076437646045 0.319312988012899 0.319312988012899;0.496926830136796 0.323380833381777 0.323380833381777;0.503013792869533 0.327398140623401 0.327398140623401;0.50902797283075 0.331366747831806 0.331366747831806;0.514971920041639 0.335288384310573 0.335288384310573;0.52084803900808 0.339164679379446 0.339164679379446;0.526658600087145 0.342997170285018 0.342997170285018;0.532405749736929 0.346787309324457 0.346787309324457;0.538091519780911 0.350536470275867 0.350536470275867;0.543717835800262 0.354245954216038 0.354245954216038;0.549286524752346 0.35791699479544 0.35791699479544;0.554799321900901 0.361550763031094 0.361550763031094;0.560257877132387 0.365148371670111 0.365148371670111;0.565663760723699 0.368710879169981 0.368710879169981;0.57101846861837 0.372239293335978 0.372239293335978;0.576323427261514 0.37573457465109 0.37573457465109;0.5815799980378 0.379197639329681 0.379197639329681;0.586789481351563 0.382629362122368 0.382629362122368;0.591953120383723 0.386030578896462 0.386030578896462;0.597072104556238 0.389402089013534 0.389402089013534;0.602147572731474 0.392744657523272 0.392744657523272;0.607180616170835 0.39605901719067 0.39605901719067;0.612172281274466 0.399345870371795 0.399345870371795;0.617123572121479 0.402605890751705 0.402605890751705;0.622035452828184 0.405839724956714 0.405839724956714;0.626908849740018 0.409047994051931 0.409047994051931;0.631744653471276 0.412231294933895 0.412231294933895;0.63654372080536 0.415390201627149 0.415390201627149;0.641306876467048 0.41852526649273 0.41852526649273;0.646034914777143 0.421637021355784 0.421637021355784;0.650728601198918 0.424725978558817 0.424725978558817;0.65538867378487 0.427792631946499 0.427792631946499;0.660015844531538 0.430837457787365 0.430837457787365;0.664610800649425 0.433860915637312 0.433860915637312;0.66917420575442 0.43686344914929 0.43686344914929;0.6737067009866 0.439845486833253 0.439845486833253;0.678208906061722 0.442807442770048 0.442807442770048;0.682681420260305 0.445749717282598 0.445749717282598;0.687124823358767 0.448672697567485 0.448672697567485;0.691539676506711 0.451576758289719 0.451576758289719;0.69592652305412 0.454462262143314 0.454462262143314;0.700285889331911 0.457329560380024 0.457329560380024;0.704618285389029 0.460178993308422 0.460178993308422;0.70892420568899 0.463010890765347 0.463010890765347;0.713204129768578 0.465825572561541 0.465825572561541;0.717458522861178 0.468623348903205 0.468623348903205;0.721687836487032 0.471404520791032 0.471404520791032;0.725892509012542 0.474169380398175 0.474169380398175;0.730072966180581 0.476918211428497 0.476918211428497;0.734229621613635 0.479651289456334 0.479651289456334;0.738362877291438 0.48236888224894 0.48236888224894;0.742473124004688 0.485071250072666 0.485071250072666;0.746560741786273 0.487758645983878 0.487758645983878;0.750626100321365 0.490431316105521 0.490431316105521;0.754669559337628 0.493089499890193 0.493089499890193;0.758691468976711 0.495733430370525 0.495733430370525;0.762692170148107 0.498363334397601 0.498363334397601;0.764404163705429 0.504432963216209 0.50097943286812;0.76611233156448 0.51043042198352 0.503581940940926;0.767816699258443 0.516358225453477 0.506171068243531;0.769517292037741 0.522218745642718 0.508747019069168;0.771214134874397 0.528014222921924 0.511309992564914;0.772907252466318 0.533746776023081 0.513860182911363;0.774596669241483 0.539418411089409 0.516397779494322;0.776282409362061 0.545031029877577 0.518922967068942;0.77796449672844 0.550586437207276 0.521435925916695;0.779642954983178 0.55608634774088 0.523936831995584;0.781317807514887 0.561532392165386 0.526425857083916;0.782989077462027 0.566926122839802 0.528903168918001;0.784656787716645 0.572269018963424 0.531368931324057;0.786320960928024 0.577562491313753 0.533823304344647;0.787981619506279 0.582807886597066 0.536266444359896;0.789638785625875 0.588006491449651 0.538698504203764;0.79129248122908 0.593159536123392 0.541119633275619;0.792942728029358 0.59826819788562 0.54352997764733;0.794589547514695 0.603333604159835 0.545929680166113;0.796232960950861 0.608356835431054 0.548318880553316;0.797872989384615 0.613338927936973 0.550697715499356;0.799509653646852 0.618280876163953 0.553066318754972;0.801142974355687 0.623183635164832 0.555424821218987;0.802772971919486 0.628048122713892 0.557773351022717;0.804399666539844 0.632875221312728 0.560112033611204;0.806023078214501 0.637665780059447 0.562440991821405;0.807643226740215 0.642420616392417 0.564760345957481;0.809260131715577 0.647140517718681 0.56707021386331;0.810873812543777 0.651826242936254 0.569370710992362;0.81248428843532 0.656478523858612 0.571661950475029;0.814091578410694 0.661098066548959 0.573944043183551;0.815695701302994 0.665685552571153 0.576217097794616;0.817296675760492 0.670241640163568 0.57848122084975;0.81889452024917 0.674766965341621 0.580736516813593;0.820489253055203 0.679262142934176 0.582983088130137;0.822080892287403 0.683727767558638 0.58522103527703;0.823669455879614 0.688164414539076 0.587450456818008;0.825254961593074 0.69257264077142 0.589671449453553;0.82683742701873 0.696952985539403 0.591884108069832;0.828416869579514 0.701305971284629 0.594088525786005;0.829993306532582 0.705632104333885 0.596284793999944;0.831566754971515 0.709931875586564 0.59847300243246;0.833137231828481 0.714205761164838 0.600653239170064;0.834704753876358 0.718454223029022 0.602825590706348;0.836269337730828 0.722677709560372 0.60499014198202;0.837830999852432 0.726876656113411 0.60714697642366;0.839389756548585 0.731051485539701 0.609296175981238;0.84094562397557 0.73520260868484 0.611437821164447;0.842498618140485 0.739330424860348 0.613571991077896;0.844048754903172 0.743435322291975 0.615698763455199;0.845596049978098 0.74751767854584 0.617818214692015;0.847140518936221 0.75157786093375 0.619930419878067;0.848682177206813 0.755616226898907 0.622035452828184;0.850221040079263 0.759633124383166 0.6241333861124;0.851757122704842 0.7636288921769 0.626224291085149;0.853290440098445 0.767603860252481 0.628308237913578;0.854821007140305 0.771558350082286 0.630385295605023;0.856348838577675 0.775492674942123 0.632455532033676;0.857873949026488 0.779407140200857 0.634519013966459;0.859396352972985 0.78330204359702 0.636575807088154;0.860916064775327 0.787177675503096 0.638625976025797;0.862433098665168 0.791034319178155 0.640669584372373;0.863947468749212 0.794872251009454 0.642706694709832;0.865459189010745 0.79869174074359 0.644737368631448;0.866968273311143 0.802493051707749 0.646761666763555;0.868474735391348 0.806276441021567 0.648779648786657;0.869978588873335 0.81004215980009 0.650791373455968;0.871479847261545 0.813790453348271 0.652796898621365;0.872978523944303 0.817521561347451 0.654796281246802;0.874474632195206 0.821235718034209 0.656789577429185;0.875968185174501 0.824933152371968 0.658776842416744;0.877459195930429 0.828614088215704 0.66075813062689;0.878947677400562 0.832278744470104 0.662733495663611;0.880433642413107 0.83592733524148 0.664702990334388;0.881917103688197 0.839560069983745 0.666666666666667;0.883398073839164 0.843177153638724 0.668624575923897;0.884876565373788 0.846778786771073 0.670576768621147;0.886352590695531 0.850365165698055 0.672523294540305;0.887826162104748 0.853936482614409 0.6744642027449;0.889297291799888 0.857492925712544 0.676399541594523;0.890765991878665 0.861034679298255 0.678329358758891;0.892232274339227 0.864561923902179 0.680253701231545;0.893696151081292 0.868074836387179 0.682172615343201;0.895157633907282 0.871573590051819 0.684086146774769;0.896616734523426 0.875058354730133 0.685994340570035;0.898073464540857 0.878529296887814 0.68789724114804;0.899527835476694 0.881986579715012 0.689794892315138;0.900979858755096 0.885430363215863 0.691687337276764;0.902429545708318 0.888860804294893 0.693574618648914;0.903876907577734 0.892278056840442 0.695456778469341;0.905321955514863 0.895682271805211 0.697333858208478;0.906764700582363 0.899073597284078 0.699205898780101;0.908205153755026 0.902452178589272 0.701072940551735;0.909643325920746 0.905818158323023 0.702935023354807;0.911079227881486 0.909171676447799 0.704792186494566;0.912512870354217 0.912512870354217 0.706644468759756;0.913944263971857 0.913944263971857 0.712158070688705;0.915373419284188 0.915373419284188 0.717629312434602;0.916800346758766 0.916800346758766 0.723059155590786;0.918225056781811 0.918225056781811 0.728448525911036;0.919647559659095 0.919647559659095 0.733798315152237;0.921067865616804 0.921067865616804 0.739109382797;0.922485984802405 0.922485984802405 0.744382557665655;0.923901927285483 0.923901927285483 0.749618639426184;0.925315703058582 0.925315703058582 0.754818400009873;0.926727322038023 0.926727322038023 0.75998258493979;0.928136794064718 0.928136794064718 0.765111914578557;0.92954412890497 0.92954412890497 0.770207085301327;0.930949336251263 0.930949336251263 0.775268770599375;0.932352425723038 0.932352425723038 0.780297622119257;0.933753406867467 0.933753406867467 0.785294270642075;0.935152289160203 0.935152289160203 0.790259327007008;0.936549082006136 0.936549082006136 0.795193382982951;0.937943794740124 0.937943794740124 0.800097012091765;0.939336436627724 0.939336436627724 0.804970770386398;0.940727016865912 0.940727016865912 0.809815197186847;0.942115544583787 0.942115544583787 0.814630815776737;0.943502028843273 0.943502028843273 0.819418134063051;0.94488647863981 0.94488647863981 0.824177645201369;0.946268902903032 0.946268902903032 0.828909828188793;0.947649310497441 0.947649310497441 0.833615148426583;0.949027710223069 0.949027710223069 0.838294058254367;0.950404110816136 0.950404110816136 0.842946997457655;0.951778520949688 0.951778520949688 0.847574393750293;0.953150949234246 0.953150949234246 0.852176663233321;0.954521404218424 0.954521404218424 0.856754210831658;0.955889894389557 0.955889894389557 0.861307430709894;0.957256428174314 0.957256428174314 0.865836706668399;0.958621013939301 0.958621013939301 0.870342412520888;0.959983659991659 0.959983659991659 0.874824912454475;0.961344374579655 0.961344374579655 0.879284561373212;0.962703165893265 0.962703165893265 0.883721705226018;0.964060042064747 0.964060042064747 0.888136681319876;0.965415011169212 0.965415011169212 0.892529818619066;0.96676808122518 0.96676808122518 0.896901438031227;0.968119260195139 0.968119260195139 0.901251852680916;0.969468555986088 0.969468555986088 0.905581368171345;0.970815976450078 0.970815976450078 0.909890282834906;0.972161529384745 0.972161529384745 0.914178887973074;0.973505222533836 0.973505222533836 0.918447468086219;0.974847063587731 0.974847063587731 0.922696301093858;0.976187060183953 0.976187060183953 0.926925658545813;0.977525219907679 0.977525219907679 0.931135805824741;0.978861550292238 0.978861550292238 0.935327002340459;0.980196058819607 0.980196058819607 0.939499501716467;0.9815287529209 0.9815287529209 0.943653551969043;0.982859639976851 0.982859639976851 0.947789395679278;0.984188727318288 0.984188727318288 0.951907270158387;0.98551602222661 0.98551602222661 0.956007407606601;0.986841531934245 0.986841531934245 0.960090035265961;0.988165263625116 0.988165263625116 0.964155375567286;0.989487224435092 0.989487224435092 0.968203646271586;0.990807421452438 0.990807421452438 0.972235060606176;0.992125861718258 0.992125861718258 0.976249827395732;0.993442552226933 0.993442552226933 0.980248151188512;0.994757499926555 0.994757499926555 0.984230232377972;0.996070711719353 0.996070711719353 0.988196267319958;0.997382194462116 0.997382194462116 0.992146448445691;0.998691954966612 0.998691954966612 0.996080964370718;1 1 1],...
    'FontName','Times New Roman','FontSize',15,'Layer','top');
% Create colorbar
colorbar(axes1);


%%
P_fsw=[];
kx=[];
for i= 1:1:length(fsw_tot)
[M,k] = min(P_tot(i,:)) ;
P_fsw=[P_fsw M ];
kx =[kx k];
end

%%
% plot(fsw_tot/1e3, P_fsw)
% yline(1500)



% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create plot
plot1 = plot(fsw_tot/1e3, P_fsw,'DisplayName','Inverter Loss','Marker','x','LineWidth',2,...
    'Color',[1 0 0]);

% The following line demonstrates an alternative way to create a data tip.
% datatip(plot1,18.5,1504.62051282051);
% Create datatip
datatip(plot1,'DataIndex',28,'Location','southeast');

% Create yline
yline(1500,'DisplayName','Loss Limitation','Parent',axes1,'LineWidth',2,...
    'Alpha',1);

% Create ylabel
ylabel({'Losses (W)'});

% Create xlabel
xlabel({'Switching Frequency'});

box(axes1,'on');
grid(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.5,...
    'GridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'GridLineWidth',1,'MinorGridAlpha',0.5,'MinorGridColor',...
    [0.0745098039215686 0.623529411764706 1],'MinorGridLineWidth',1,...
    'XMinorGrid','on','YMinorGrid','on');
% Create legend
legend1 = legend(axes1,'show');
set(legend1,...
    'Position',[0.229166670764485 0.778174606154836 0.296428565308452 0.110714282734054]);

% Create textarrow
annotation(figure1,'textarrow',[0.639285714285714 0.619642857142854],...
    [0.326190476190477 0.459523809523811],...
    'String',{'Maximum Switching Frequency'},...
    'FontSize',15,...
    'FontName','Times New Roman');

%%

save('savefsw_tot.mat','fsw_tot');
save('savePfsw.mat','P_fsw');

%%



% Create figure
figure1 = figure;

% Create axes
axes1 = axes('Parent',figure1);
hold(axes1,'on');

% Create plot
plot1 = plot(fsw_tot/1e3, kx,'DisplayName','Inverter Loss','Marker','x','LineWidth',2,...
    'Color',[1 0 0]);

% Create ylabel
ylabel({'Number of Parallel Die'});

% Create xlabel
xlabel({'Switching Frequency'});

box(axes1,'on');
grid(axes1,'on');
hold(axes1,'off');
% Set the remaining axes properties
set(axes1,'FontName','Times New Roman','FontSize',15,'GridAlpha',0.5,...
    'GridColor',[0.301960784313725 0.745098039215686 0.933333333333333],...
    'GridLineWidth',1,'MinorGridAlpha',0.5,'MinorGridColor',...
    [0.0745098039215686 0.623529411764706 1],'MinorGridLineWidth',1,...
    'XMinorGrid','on','YMinorGrid','on');
% Create legend