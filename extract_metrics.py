#!/usr/bin/env python3
import re
import sys

def extract_epoch_metrics():
    """CSV 파일에서 epoch별 메트릭을 추출합니다."""
    
    metrics_file = "./exp/lightning_logs/version_17/metrics.csv"
    
    print("📊 30 Epoch까지의 훈련 메트릭 분석")
    print("=" * 60)
    
    try:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📁 파일: {metrics_file}")
        print(f"📈 총 라인 수: {len(lines)}")
        
        # 헤더 파싱
        header = lines[0].strip().split(',')
        print(f"📋 컬럼: {header}")
        
        # Epoch별 데이터 수집
        epoch_data = {}
        
        for i, line in enumerate(lines[1:], 1):
            if i > 1000:  # 처음 1000줄만 처리
                break
                
            parts = line.strip().split(',')
            if len(parts) >= 7:
                try:
                    epoch = float(parts[6]) if parts[6] else 0
                    if epoch > 0 and epoch <= 30:
                        if epoch not in epoch_data:
                            epoch_data[epoch] = []
                        
                        # Training Loss 추출
                        train_loss = parts[2] if len(parts) > 2 and parts[2] else None
                        # Validation Loss 추출  
                        val_loss = parts[4] if len(parts) > 4 and parts[4] else None
                        
                        if train_loss or val_loss:
                            epoch_data[epoch].append({
                                'train_loss': float(train_loss) if train_loss else None,
                                'val_loss': float(val_loss) if val_loss else None
                            })
                except (ValueError, IndexError):
                    continue
        
        print(f"\n🔄 수집된 Epoch 데이터: {len(epoch_data)} epochs")
        
        # 결과 출력
        print(f"\n📊 Epoch별 메트릭 요약:")
        print("-" * 80)
        print(f"{'Epoch':<8} {'Train Loss':<15} {'Val Loss':<15} {'Data Points':<12}")
        print("-" * 80)
        
        for epoch in sorted(epoch_data.keys()):
            data_points = epoch_data[epoch]
            
            # Training Loss 통계
            train_losses = [d['train_loss'] for d in data_points if d['train_loss'] is not None]
            train_avg = sum(train_losses) / len(train_losses) if train_losses else None
            
            # Validation Loss 통계
            val_losses = [d['val_loss'] for d in data_points if d['val_loss'] is not None]
            val_avg = sum(val_losses) / len(val_losses) if val_losses else None
            
            train_str = f"{train_avg:.4f}" if train_avg else "N/A"
            val_str = f"{val_avg:.4f}" if val_avg else "N/A"
            
            print(f"{epoch:<8.1f} {train_str:<15} {val_str:<15} {len(data_points):<12}")
        
        # 전체 통계
        all_train_losses = []
        all_val_losses = []
        
        for epoch_data_list in epoch_data.values():
            for data in epoch_data_list:
                if data['train_loss'] is not None:
                    all_train_losses.append(data['train_loss'])
                if data['val_loss'] is not None:
                    all_val_losses.append(data['val_loss'])
        
        print(f"\n📈 전체 통계 (Epoch 1-30):")
        print("-" * 40)
        
        if all_train_losses:
            print(f"🏋️ Training Loss:")
            print(f"   - 데이터 포인트: {len(all_train_losses)}")
            print(f"   - 최소값: {min(all_train_losses):.4f}")
            print(f"   - 최대값: {max(all_train_losses):.4f}")
            print(f"   - 평균값: {sum(all_train_losses)/len(all_train_losses):.4f}")
        
        if all_val_losses:
            print(f"\n✅ Validation Loss:")
            print(f"   - 데이터 포인트: {len(all_val_losses)}")
            print(f"   - 최소값: {min(all_val_losses):.4f}")
            print(f"   - 최대값: {max(all_val_losses):.4f}")
            print(f"   - 평균값: {sum(all_val_losses)/len(all_val_losses):.4f}")
        
        print(f"\n✅ 분석 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_epoch_metrics()
