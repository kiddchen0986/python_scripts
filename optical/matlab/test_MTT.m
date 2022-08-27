function test_MTT
tic
% Test settings
sensorType = 'P2';
%edgeDetectThreshold = 20;
edgeDetectThreshold = 20;
%uniformityThreshold = 0.9;
uniformityThreshold = 0.9;
%offSetThreshold = 2.0;
offSetThreshold = 2.0;
%contrastThreshold = 0.55;
contrastThreshold = 0.55;
%Th_mul_factor = 0.8;
Th_mul_factor = 0.8;
plotFlag = 0;

% sensorNo = [3:5 7:10];
% nImages = numel(sensorNo);
% pStr = 'K:\\R-D_Core\\Projects\\JDV-10050 Islay\\Transducer - TT\\Testing\\2019_01_23_P2_Visera_sample_test\\2018_12_21_P2_medium_height\\P2_%03d\\Distance_0900um';
% root_dir = sprintf(pStr, sensorNo(ii));
% root_dir =  'K:\R-D_Core\Projects\JDV-10050 Islay\ASIC\Prod_Test\SuperPix_Visera_CP_Test\Test_Image_from_SuperPix\SP_DB No optical\185K081_#4_NO';
% d = dir(fullfile(root_dir, 'OVT_1.png'));

root_dir =  'C:\Octave\TestImages';
d = dir(fullfile(root_dir, '*.png'));
nImages = numel(d);

for ii=1:nImages
    im_native = imread(fullfile(d(ii).folder, d(ii).name));
    % Scale to 0-255 if needed.
    switch class(im_native)
        case 'uint16'
            im = double(im_native)*(2^8-1)/(2^16-1);
        case 'uint8'
            im = double(im_native)*(2^8-1)/(2^8-1);
        otherwise
            error('Image type: %s not implemented yet', class(im_native))
    end
    
    [sub_im, x, y] = extractSubImages(im, sensorType);
    %     gaussian_fit_data(:,:,ii) = gaussian(sub_im);
    number_failed_uf(ii) = uniformity(sub_im, uniformityThreshold, plotFlag);  
    number_failed_ed(ii) = edge_detection(sub_im, edgeDetectThreshold, plotFlag);
    number_failed_off(ii) = offset_detection(sub_im, offSetThreshold, plotFlag);
    [failed_av_contrast(ii),number_failed_indvl_contrast(ii), mean_rms_norm(ii)] = contrast_detection(sub_im, contrastThreshold, Th_mul_factor, plotFlag);


end

% Write results  to text file
formatSpec = '%s, uniformity, %d, edge, %d, offset, %d, contrast, %d, %d\r\n';
fid = fopen('MTT_result.txt', 'w');
if fid
    for ii=1:nImages
    fprintf(fid, formatSpec, d(ii).name, number_failed_uf(ii),...
        number_failed_ed(ii), number_failed_off(ii),...
        failed_av_contrast(ii), number_failed_indvl_contrast(ii));
    end
    fclose(fid);
end

toc
end

%%%%%%%%%%%%%%%%%%%%%
% Sub-functions
%%%%%%%%%%%%%%%%%%%%%

function [sub_im, x, y] = extractSubImages(im, sensorType)

switch sensorType
    case 'P1'
        xs = round(90.85)-0.5;
        ys = round(50.95)-0.5;
        xp = 102.667;
        yp = 88.91;
        s = 26;
        rows = 12;
        cols = 18;
        no_sub = 222;
        alternatingNumberOfColumns = 1;
    case 'P2'
        xs = 49.5;
        ys = 44.5;
        xp =  104;
        yp = 90;
        s = 32;
        rows = 12;
        cols = 18;
        no_sub = 216;
        alternatingNumberOfColumns = 0;
    otherwise
        error('Wrong sensor type')
end

sub_im = zeros(s, s, no_sub);
counter = 0;

for yi = 1: rows
    if mod(yi,2)==1
        colstemp = cols;   % if no of columns 18, colstemp = cols;
    else
        colstemp =cols + alternatingNumberOfColumns;   % if no of columns 18-19, colstemp =cols+1;
    end
    for xi = 1: colstemp
        
        counter = counter+1;
        % Calculate microlens center position in x and y
        x(counter) = xs + xp * (xi-1);
        y(counter) = ys +  yp * (yi-1);
        
        % Shift every second row half pitch in x
        % if no of columns 18-19,  x(counter) = x(counter) - xp/2;
        % if no of columns 18,  x(counter) = x(counter) + xp/2;
        if mod(yi,2)==0
            if alternatingNumberOfColumns
                x(counter) = x(counter) - xp/2;
            else
                x(counter) = x(counter) + xp/2;
            end
        end
        
        % Calculate index for subimage extraction
        idx = -(s-1)/2:(s-1)/2;
        xIdx = round(x(counter) + idx);
        yIdx = round(y(counter) + idx);
        sub_im(:,:,counter) = im(yIdx, xIdx);
    end
end

end


% Fit a Gaussian function of the form g = x1 + x2*exp(-2*((x-x3)/x4)^2) to the input data x,y.

function gaussian_fit_data = gaussian(sub_im_all)


% Gaussian fit parameters
mode = 2;
k = size(sub_im_all, 1);
xCoordinate = -(k-1)/2:(k-1)/2;

% Loop over all subimages
for ii=1:size(sub_im_all, 3)
    sub_im = sub_im_all(:,:,ii);
    % Extract cross section in x and y.
    csX = mean(sub_im(k/2:k/2+1,:), 1);
    csY = mean(sub_im(:,k/2:k/2+1), 2);
    
    % Gaussian fit to cross section of sub image in the x-direction
    offsetStartValue = 0;
    amplitudeStartValue = max(csX);
    xOffsetStartValue = 0;
    widthStartValue = 1;
    gpar0 = [offsetStartValue amplitudeStartValue xOffsetStartValue widthStartValue]; %initial values
    options = optimset('fminsearch');
    options = optimset(options, 'TolFun', 1e-8, 'TolX', 1e-8,...
        'MaxIter', 1e8, 'MaxFunEvals', 1e8);
    gparX = fminsearch(@(x) fitgaussian(x, xCoordinate, csX, mode), gpar0, options);
    gFitX = gparX(1) + gparX(2)*exp(-2*((xCoordinate - gparX(3))/gparX(4)).^2);
    
    % Gaussian fit to cross section of sub image in the y-direction
    offsetStartValue = 0;
    amplitudeStartValue = max(csY);
    xOffsetStartValue = 0;
    widthStartValue = 1;
    gpar0 = [offsetStartValue amplitudeStartValue xOffsetStartValue widthStartValue]; %initial values
    gparY = fminsearch(@(x) fitgaussian(x, xCoordinate, csY, mode), gpar0, options);
    gFitY = gparY(1) + gparY(2)*exp(-2*((xCoordinate - gparY(3))/gparY(4)).^2);
    
    cmFigure('Gaussian');clf;
    plot(xCoordinate, csX, 'b', xCoordinate, csY, 'r',...
        xCoordinate, gFitX, 'b--', xCoordinate, gFitY, 'r--', 'linewidth', 2)
    grid on
    legend('Cross Section X', 'Cross Section Y', 'Fit X', 'Fit Y')
    
    % Save Gaussian fit data
    gaussian_fit_data(ii,:) = [gparX gparY];
end

end


%%% edge detection %%%

%Check for edges where the pixel to pixel difference is
%       larger than threshold, in x or y direction

function number_failed = edge_detection(sub_im_all, threshold, plotFlag)

nSubImages = size(sub_im_all, 3);

for ii=1:nSubImages
    sub_im = sub_im_all(:,:,ii);
    %y_diff(ii) = max(abs(diff(sub_im, 1,1)), [], 'all');
    %x_diff(ii) = max(abs(diff(sub_im, 1,2)), [], 'all');
    y_diff(ii) = max(max(abs(diff(sub_im, 1,1))));  % Octave style
    x_diff(ii) = max(max(abs(diff(sub_im, 1,2))));  % Octave style
end

failed_x = x_diff > threshold;
failed_y = y_diff > threshold;
failed = failed_x | failed_y;
number_failed = sum(failed);
disp(["Edge detect: Number of failed subimages: ", num2str(number_failed)]);
disp(["Edge detect: limit: ", num2str(threshold)]);

end


%%% Uniformity detection %%%

function number_failed_uf = uniformity(sub_im_all, uniformityThreshold, plotFlag)
n = 100;

nSubImages = size(sub_im_all, 3);
for ii=1:nSubImages
    sub_im = sub_im_all(:,:,ii);
    %     sub_im_mean(ii) = mean(sub_im(:));
    sub_im_sorted = sort(sub_im(:), 'descend');
    sub_im_median(ii) = median(sub_im_sorted(1:n));
end

threshold = uniformityThreshold*max(sub_im_median);

failed_uf = sub_im_median < threshold;
number_failed_uf = sum(failed_uf);
disp(["Uniformity: Number of failed subimages: ", num2str(number_failed_uf)]);
disp(["Uniformity: limit: ", num2str(uniformityThreshold)]);

end


%%% off-set detection %%%

%   Calculate the average position for pixels values higher than the k:threshold highest pixels,
%   to indicate if lens is positioned incorrect compared to where it is suppossed to be

function [number_failed_off, x_off, y_off]  = offset_detection(sub_im_all, max_offset, plotFlag)
s = size(sub_im_all, 1);
xCoordinate = -(s-1)/2:(s-1)/2;
[X, Y] = meshgrid(xCoordinate);

nSubImages = size(sub_im_all, 3);

for ii=1:nSubImages
    sub_im = sub_im_all(:,:,ii);
    %sub_im = circshift(sub_im, [1 1]);
    tot_mass = sum(sub_im(:));
    x_off(ii) = sum(X(:).*sub_im(:)) / tot_mass;
    y_off(ii) = sum(Y(:).*sub_im(:)) / tot_mass;
    
end

x_failed_off = abs(x_off) > max_offset;
y_failed_off = abs(y_off) > max_offset;
failed_off = x_failed_off | y_failed_off;
number_failed_off = sum(failed_off);
disp(["Offset: Number of failed subimages: ", num2str(number_failed_off)]);
disp(["Offset: limit: ", num2str(max_offset)]);

end


%%% Contrast %%%

% Calculate the contrast as RMS (Root Mean Square) for each sub image
% Mark the ones with contrast lower than  threshold' of max contrast as failing

function [failed_av_contrast,number_failed_indvl_contrast, mean_rms_norm] = contrast_detection(sub_im_all, threshold_av, Th_mul_factor, plotFlag)

nSubImages = size(sub_im_all, 3);

for ii=1:nSubImages
    sub_im = sub_im_all(:,:,ii);
    im_av(ii) = mean(sub_im(:));
    rms(ii) = std(sub_im(:));
end
% Normalize with average value
rms_norm = rms ./ im_av;
mean_rms_norm = mean(rms_norm);

threshold_indvl = Th_mul_factor * mean_rms_norm;

failed_av = mean_rms_norm < threshold_av;
failed_indvl = rms_norm < threshold_indvl;

failed_av_contrast = sum(failed_av);
number_failed_indvl_contrast = sum(failed_indvl);
disp(["Contrast: Number of average failed subimages: ", num2str(failed_av_contrast)]);
disp(["Contrast: Number of individual failed subimages: ", num2str(number_failed_indvl_contrast)]);
disp(["Contrast: average limit: ", num2str(threshold_av)]);
disp(["Contrast: individual limit: ", num2str(Th_mul_factor)]);

end

